import socket
from threading import *

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 8000
print (host)
print (port)
serversocket.bind((host, port))

class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        print("Connection Received From:\t> " + str(self.addr))
        self.start()

    def run(self):
        try:
            while 1:
                data = self.sock.recv(1024).decode()
                if data:
                    print('Client sent:' + data)
                    self.sock.send(b'Oi you sent something to me')
                else:
                    self.sock.send(b'No info sent')
        except:
            self.sock.close()
            print("Connection Closed on Address\t> " + str(self.addr))

serversocket.listen(5)
print ('server started and listening')
while 1:
    clientsocket, address = serversocket.accept()
    client(clientsocket, address)