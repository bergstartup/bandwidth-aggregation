"""
checked files:
obtain.py all_checked [still_complete:get_nics()]
sockops.py all_checked
fileops.py all_checked [check the issue]

integrated testing:
Finished
check with multiple nics in windows
check custom exception raise and handling in session managers

Issues:
fileops.py
Thread exception handling

Enhancments:
1.Add file control
2.Make UI
3.Access from cmd
4.Working in linux
5.Variable buff size
6.Resume incomplete download 

code to complete:
bandwidth_check.py
"""

#ports explanation
#udp 10,000 server listen for request
#udp 10,001-10,010 client udp request send
#tcp 1000-1010 client-server interaction



"""
Completed integration testing on the module, working fine
"""

"""
#fileops.py [check_file,read_file,write_file]
import fileops
print(fileops.check_file("suva.mp4"))
print(fileops.check_file("suva_modified.mp4"))
readers=fileops.read_file("suva.mp4",[1,1,1],1024)
print(readers)
file_data=[]
for reader in readers:
    file_data.append([])
    for data in reader:
        file_data[-1].append(data)
    print("pointer position : ",reader.file_ptr.tell())
fileops.write_file("suva_modified.mp4",file_data)
print(fileops.check_file("suva_modified.mp4"))

--
included for verbosing in read_file
#for verbose
print("filename : ",filename)
print("ratio : ",ratio)
print("total of ratio : ",total)
print("size of file : ",size)
print("chunk : ",chunk)
for i in readers:
    print("start : ",i.start)
    print("end : ",i.end)
--
--output--
1
0
filename :  suva.mp4
ratio :  [1, 1, 1]
total of ratio :  3
size of file :  12861924
chunk :  4287308
start :  0
end :  4287308
start :  4287309
end :  8574617
start :  8574618
end :  12861924
[<fileops.read_class object at 0x7fa65e38d358>, <fileops.read_class object at 0x7fa65e38d2e8>, <fileops.read_class object at 0x7fa65d259d68>]
pointer position :  4287309
pointer position :  8574618
pointer position :  12861924
1 #File is error free
"""


"""
sockops.py [udp_send,udp_recv]
import socket
import sockops
import threading
import time
def op1(sock):
    data=sockops.udp_recv(sock,1024)
    print(data)
    
s1=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s1.bind(("127.0.0.1",500))
s2=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s2.bind(("127.0.0.1",502))

t1=threading.Thread(target=op1,args=(s2,))
t1.start()
sockops.udp_send(s1,"hello",("127.0.0.1",502))
s1.close()
s2.close()
--output--
(('127.0.0.1', 500), 'hello')
"""


"""
sockops.py [tcp_send,tcp_recv]
import socket
import sockops
import threading
import time
def op1(sock):
    sock.listen(1)
    print("listening")
    client,addr=sock.accept()
    data=sockops.tcp_recv(client,1024)
    print(data)
    
s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.bind(("127.0.0.1",500))
s2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2.bind(("127.0.0.1",502))

t1=threading.Thread(target=op1,args=(s2,))
t1.start()
time.sleep(2)
s1.connect(("127.0.0.1",502))
sockops.tcp_send(s1,"hello")
s1.close()
s2.close()
--output--
listening
hello
"""


"""
obtain.py
import obtain

print(obtain.get_token())
print(obtain.get_port())
print(obtain.get_port(True))
--output--
client#2020-01-19 19:08:53.220132
1000
(<socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('0.0.0.0', 1000)>, 1000)
"""
