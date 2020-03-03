#Sock operations send/recieve
def tcp_send(socket,msg):
    if type(msg)==int:
        data=str(msg).encode()
    else:
        try:
            data=msg.encode()
        except:
            data=msg
    socket.send(data)

def tcp_recv(socket,buff_size,file=False):
    data=socket.recv(buff_size)
    if file:
        return data
    return data.decode()

def udp_send(socket,msg,node):
    try:
        data=msg.encode()
    except:
        data=str(msg).encode()
    socket.sendto(data,node)

def udp_recv(socket,buff_size):
   data,client=socket.recvfrom(buff_size)
   return client,data.decode()
