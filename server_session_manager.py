import threading
import worker
import bandwidth_check
import sockops
import fileops
import pickle
class SSmanager(threading.Thread):
    def __init__(self,token,port,socket):
        threading.Thread.__init__(self)
        self.token=token
        self.port=port
        self.socket=socket
        self.clients=[]
        self.mutex=0
        self.workers=[]
        self.file_data=None
        self.bandwidth_ratio=None
        self.buff_size=None
        
    def run(self):
        self.recv_connections()
        #self.verbose()
        self.create_workers()
        self.start_work()
        self.await_completion()
        self.finished()
        self.terminate()

    def verbose(self):
        print("From server session manager")
        print("Token : ",self.token)
        print("Server Port : ",self.port)
        print("Mode : ",self.mode)
        print("Filename : ",self.filename)
        
    def recv_connections(self):
        self.socket.listen(1)
        while True:
            client,addr=self.socket.accept()
            data=sockops.tcp_recv(client,1024)
            token,id_all=data.split(",")
            if self.token==token:
                sockops.tcp_send(client,"1")
            else:
                sockops.tcp_send(client,"-1")
            self.clients.append(client)
            if id_all.split("/")[0]==id_all.split("/")[1]:
                break
        mode=int(sockops.tcp_recv(self.clients[0],1024))
        self.buff_size=int(sockops.tcp_recv(self.clients[0],1024))
        self.mode=1-mode #change in server mode
        filename=sockops.tcp_recv(self.clients[0],1024)

        #Check for the presence of file in the server if mode is upload[i.e,self.mode=1]
        if self.mode==1:
            #self.bandwidth_ratio=pickle.load(sockops.tcp_recv(self.client[0],1024))
            self.bandwidth_ratio=bandwidth_check.get(self.clients)
            status=fileops.check_file(filename)
            if status==0:
                sockops.tcp_send(self.clients[0],"0")
                self.terminate(404)
            else:
                self.filename=filename
                self.filesize=fileops.get_size(filename)
                sockops.tcp_send(self.clients[0],"1")
                sockops.tcp_send(self.clients[0],str(self.filesize))
        else:
            self.filename=filename
            self.filename=self.token.split(" ")[0]+self.filename#change in filename while storing in server only during download
            sockops.tcp_send(self.clients[0],"1")
        

    def create_workers(self):
        for num,sock in enumerate(self.clients):
            self.workers.append(worker.worker(self,num,sock))

    def start_work(self):
        #download
        if self.mode==0:
            self.file_data=[[] for i in self.clients]
        #upload
        else:
            self.file_data=fileops.read_file(self.filename,self.bandwidth_ratio,self.buff_size)
        #Intiate workers
        for worker in self.workers:
            worker.start()

    def await_completion(self):
        while self.mutex!=len(self.clients):
            continue

    def finished(self):
        if self.mode==0:
            fileops.write_file(self.filename,self.file_data)

    def terminate(self,error_code=None):
        #Kill all thread and objects
        del self.workers
        del self.file_data
        self.socket.close()
        del self.socket
        del self.clients
        del self
        if error_code is None:
            print("Transfer is complete")
        elif error_code==404:
            raise FileNotFoundError
