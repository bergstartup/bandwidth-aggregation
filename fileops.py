#File operation
import os

def check_file(filename):
    try:
        f=open(filename,"rb")
        f.close()
        return 1
    except:
        return 0
    
def write_file(filename,filedata):
    f=open(filename,"wb")
    for partition in filedata:
        for data in partition:
            f.write(data)
    f.flush()
    f.close()

def get_size(filename):
    return os.stat(filename).st_size

def read_file(filename,ratio,buffsize):
    total=sum(ratio)#Summing up all ratio
    size=get_size(filename)#Getting file size
    chunk=size//total #Calc each chunk size
    ptr_position=0 #Intial size
    readers=[]#Collect reader objs for nic
    for i in range(len(ratio)-1):
        start=ptr_position
        end=start+chunk*ratio[i]
        readers.append(read_class(filename,start,end,buffsize))
        ptr_position=end+1
    readers.append(read_class(filename,ptr_position,size,buffsize))
    return readers

class read_class:
    def __init__(self,filename,start,end,buffsize):
        self.filename=filename
        self.start=start
        self.end=end
        self.buff=buffsize
    def __iter__(self):
        self.file_ptr=open(self.filename,"rb")
        self.file_ptr.seek(self.start)
        return self
    def __next__(self):
        if self.file_ptr.tell()<self.end: #--issue-- last bit alone wont be recn clash with final pointer
            if self.file_ptr.tell()+self.buff<=self.end: 
                data=self.file_ptr.read(self.buff)
            else:
                data=self.file_ptr.read(self.end-self.file_ptr.tell()+1)
            return data
        else:
            raise StopIteration
