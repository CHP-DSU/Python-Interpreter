
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "172.16.68.106"
port =8000
s.connect((host,port))

def ts(str):
   s.send(b'hello') 
   data = s.recv(1024).decode()
   print (data)
try:
    while 2:
        r = input('enter')
        ts(s)
except:
    s.close ()