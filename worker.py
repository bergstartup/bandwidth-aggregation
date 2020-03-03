import sockops
import socket
import threading
import sys
class worker(threading.Thread):
    def __init__(self,session_manager,id_,socket,client=False):
        threading.Thread.__init__(self)
        self.socket=socket
        self.session_manager=session_manager
        self.id_=id_
        self.client=client
    def run(self):
        if self.session_manager.mode==0:
            self.download()
        else:
            self.upload()

    def download(self):
        file_data=[]
        #Sync part
        self.socket.settimeout(10.0)
        while True:
            try:
                sockops.tcp_send(self.socket,"sync")
                data=sockops.tcp_recv(self.socket,self.session_manager.buff_size,True)#S_file recv not to be decoded
                break
            except socket.timeout:
                continue
        #End of sync part
        while data:
            if self.client:
                self.session_manager.completed_frames_socket[self.id_]+=1
            file_data.append(data)
            data=sockops.tcp_recv(self.socket,self.session_manager.buff_size,True) #file recv not to be decoded
        self.session_manager.file_data[self.id_]=file_data
        self.session_manager.mutex+=1
        
    def upload(self):
        sockops.tcp_recv(self.socket,1024)#sync part
        for data in self.session_manager.file_data[self.id_]:
            if self.client:
                self.session_manager.completed_frames_socket[self.id_]+=1
            sockops.tcp_send(self.socket,data)
        self.session_manager.mutex+=1
