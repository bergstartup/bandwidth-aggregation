#Server trigger
import obtain 
import server_session_manager
import time 
import threading
import socket
import sockops

#Main func
print("Server ready")#for verbose
while True:
    trigger_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    trigger_sock.bind(("0.0.0.0",10000))
    client,token=sockops.udp_recv(trigger_sock,1024)
    print("triggered")
    try:
        sock,port=obtain.get_port(True)
    except:
        print("All ports busy")
        continue
    sockops.udp_send(trigger_sock,port,client)
    obj=server_session_manager.SSmanager(token,port,sock)
    obj.start()
