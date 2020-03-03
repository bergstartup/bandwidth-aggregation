import datetime
import socket
import subprocess
import re
def get_nics():
    #Parse ipconfig for windows and ifconfig for linux
    try:
        cmd=['ipconfig']
        output=subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]   
        regex="IPv4\saddress\D*[0-2][0-9][0-9][.]\S+"
        ipv4=re.findall(regex,output.decode())
    except:
        cmd=['ifconfig']
        output=subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
        regex="inet\s[0-2][0-9][0-9][.]\S+"
        ipv4=re.findall(regex,output.decode())
    regex="[0-9]\S+"
    ips=list(map(lambda x:re.findall(regex,x)[0],ipv4))
    del ips[ips.index("127.0.0.1")]
    return ips



#Yet to change for windows
def get_nics_with_ip():
    #return ['127.0.0.1']
    try:
        #For linux dict={nic:ip}
        cmd="ifconfig"
        output=subprocess.check_output(cmd).decode()
        regex1="\S+:\sflags\S+\s+\S+\s\S+\s+inet\s\S+"
        output1=re.findall(regex1,output)
        regex2="(\S+:)|(inet\s\S+)"
        output2=list(map(lambda x:re.findall(regex2,x),output1))
        nics_ip={}
        for i in output2:
            nics_ip[i[0][0][:-1]]=i[1][1][5:]
        del nics_ip['lo']
        return nics_ip
    except:
        #For windows list=[ip]
        
        cmd=['ipconfig']
        output=subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]   
        regex="IPv4\saddress\D*[0-2][0-9][0-9][.]\S+"
        ipv4=re.findall(regex,output.decode())
        regex="[0-9]\S+"
        ips=list(map(lambda x:re.findall(regex,x)[0],ipv4))
        del ips[ips.index("127.0.0.1")]
        return ips

def get_port(server=False):
    if server:
        addr="0.0.0.0"
    else:
        try:
            addr=list(get_nics_with_ip().values())[0]
        except:
            addr=get_nics_with_ip()[0]
    avb_ports=[1000+i for i in range(11)]#1000-1010
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    for port in avb_ports:
        try:
            s.bind((addr,port))
            if server:
                return s,port
            s.close()
            del s
            return port
        except OSError:
            continue
    return -1

def get_token():
    token="client#"+str(datetime.datetime.now())
    return token
