import obtain 
import client_session_manager
import time 
import copy
import threading
import fileops
"""
Required input:
1.Server ip
2.Filename
3.mode[0-download,1-upload]
Show:
Nics and bandwidth

Trigger:
client_server_manager thread
"""
#Required for UI
nics=[]
def obtain_nics():
    global nics
    while True:
        old=copy.deepcopy(nics)
        nics=obtain.get_nics()
        time.sleep(10)
        if nics!=old:
            print("Active NICS are ",nics)
            
def trigger():
    global nics
    while True:
        server_ip=input()
        filename=input("Enter filename : ")
        mode=int(input("Enter mode [0-download,1-upload] : "))
        if mode==1:
            status=fileops.check_file(filename)
            if status==0:
                print("File not found")
                continue
        token=obtain.get_token()
        port=obtain.get_port()
        nics=obtain.get_nics_with_ip() #obtain.get_nics()
        obj=client_session_manager.CSmanager(token,port,nics,mode,filename,server_ip)
        obj.start()
        time.sleep(1)

def main():
    #t1=threading.Thread(target=obtain_nics(),daemon=True)
    t2=threading.Thread(target=trigger())
    #t1.start()
    t2.start()

main()
#Make changed for UI
