"""
import worker
import bandwidth_check
import sockops
import fileops
#"""
from Algorithm import worker,bandwidth_check,sockops,fileops
import threading
import socket
import pickle
import datetime
import time
class CSmanager(threading.Thread):
    """
    Attributes and variables:
     Token*[String],Port*[int],
     NICs*[list],Sockets[list],Mode*[int],Filename*[String]
    """
    def __init__(self,token,port,nics,mode,filename,server_ip):
        threading.Thread.__init__(self)
        #init variables
        self.token=token
        self.port=port
        self.nics=nics
        self.mode=mode
        self.filename=filename
        self.server_ip=server_ip
        self.sockets=[]
        self.server_port=None
        self.file_data=None #List for download
        self.mutex=0 #mutex
        self.workers=[] #Workers
        self.bandwidth_ratio=bandwidth_check.get(self.nics)
        self.delay=0.5
        #Transfer efficiency calculation
        self.start_time=None
        self.end_time=None
        self.file_size=None
        self.buff_size=1024*1024 #1MB
        self.frames_count=None
        self.completed_frames_socket=None
        self.completed_frames=None
    def run(self):
        try:
            #Create sockets and store in self.sockets
            self.create_sockets()
        except OSError:
            self.terminate(202)

        time.sleep(self.delay)
        #No possibility of exception
        self.server_handshake()
        time.sleep(self.delay)
        try:
            self.init_connection()
        except:
            self.terminate(303)
        self.create_workers()
        self.start_work()
        self.await_completion()#Blocking process
        self.finished()
        self.terminate()

    def verbose(self):
        print("From client session manager")
        print("Token : ",self.token)
        print("Client Port : ",self.port)
        print("Nics : ",self.nics)
        print("Mode : ",self.mode)
        print("Filename : ",self.filename)
        print("Server ip : ",self.server_ip)
        print("Server port : ",self.server_port)

        
    def create_sockets(self):
        #Create TCP sockets
        #Windows
        if type(self.nics)==list:
            for i in self.nics:
                sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.bind((i,self.port))
                self.sockets.append(sock)
        #Linux
        else:
            for i in self.nics:
                sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, 25, i.encode())
                sock.bind((self.nics[i],self.port))
                self.sockets.append(sock)
    
    def server_handshake(self):
        udp_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp_sock.settimeout(10.0) #10sec timeout
        port=10000
        while True:
            try:
                #Windows
                if type(self.nics)==list:
                    udp_sock.bind((self.nics[0],port)) #using admin nic and port 10000 to send server request
                else:
                    udp_nic=list(self.nics.keys())[0]
                    print(self.nics[udp_nic],port)
                    udp_sock.setsockopt(socket.SOL_SOCKET,25,udp_nic.encode())
                    udp_sock.bind((self.nics[udp_nic],port))
                print("Bonded")
                sockops.udp_send(udp_sock,self.token,(self.server_ip,10000)) #Server side trigger cmd
                _,server_port=sockops.udp_recv(udp_sock,1024)
                print("Recved server port")
                udp_sock.close()
                break
            except socket.timeout:
                pass
            except OSError:
                #Change of client udp trigger port, since its under use
                port+=1
                if port>10010:
                    self.terminate(202)#Error code
        self.server_port=int(server_port)
            
    def init_connection(self):
        for num,sock in enumerate(self.sockets):
            while True:
                try:
                    sock.connect((self.server_ip,self.server_port))
                    break
                except ConnectionRefusedError:
                    pass
            msg=self.token+","+(str(num)+"/"+str(len(self.nics)-1))#token,num/len(self.nics)-1
            sockops.tcp_send(sock,msg) 
            status=sockops.tcp_recv(sock,1024)
            if int(status)==-1:
                self.terminate(101)#Error code required
                
        #Send mode and filename
        sockops.tcp_send(self.sockets[0],self.mode)
        time.sleep(self.delay)
        sockops.tcp_send(self.sockets[0],self.buff_size)
        time.sleep(self.delay)
        sockops.tcp_send(self.sockets[0],self.filename)

        """
        #sending bandwidth_ratio to server incase of download
        #cmnt if server isnt changed
        if self.mode==0:
            sockops.tcp_send(self.sockets[0],pickle.dumps(self.bandwidth_ratio))
        """
        
        confirmation=sockops.tcp_recv(self.sockets[0],1024) #Acceptance from server
        if int(confirmation)==0:
            self.terminate(404)#Takes error code
        if self.mode==0:
            self.filesize=int(sockops.tcp_recv(self.sockets[0],1024))
        else:
            self.filesize=fileops.get_size(self.filename)
            
        print("File size : ",self.filesize)
        print("Iterations : ",self.filesize//self.buff_size+1)
        self.frames_count=self.filesize//self.buff_size+1

        
    def create_workers(self):
        self.completed_frames_socket=[0 for i in self.sockets]
        print(self.completed_frames_socket)
        for num,sock in enumerate(self.sockets):
            self.workers.append(worker.worker(self,num,sock,True))

    def start_work(self):
        #download
        if self.mode==0:
            self.file_data=[[] for i in self.nics]
        #upload
        else:
            self.file_data=fileops.read_file(self.filename,self.bandwidth_ratio,self.buff_size)
            
        print("Started transfer")#for verbose
        self.start_time=datetime.datetime.now()
        for worker in self.workers:
            worker.start()
            
    def await_completion(self):
        #Use queue to check for exception in worker
        #Get data trasffered status
        while self.mutex!=len(self.nics):
            self.completed_frames=sum(self.completed_frames_socket)
            continue
        print(self.completed_frames)
        self.end_time=datetime.datetime.now()

    def finished(self):
        if self.mode==0:
            fileops.write_file(self.filename,self.file_data)
        
    def terminate(self,error_code=None):
        #Kill all threads and objects
        del self.workers
        del self.file_data
        for sock in self.sockets:
            sock.close()
        del self.sockets
        time=self.end_time-self.start_time
        del self
        if error_code is None:
            print("Transfer complete")
            print("Time for trasfer : ",time)
        elif error_code==404:
            print("File not Found")
            raise FileNotFoundError
        elif error_code==101:
            print("Token/Server Port mismatch")
            raise ConnectionError
        elif error_code==202:
            print("Client port already in use")
            raise ConnectionError
        elif error_code==303:
            print("Server can't be reached [init process]")
            raise ConnectionError
        
