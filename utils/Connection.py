import socket
from threading import Thread
from utils.MessageInfo import MessageInfo

class Connection:
    def __init__(self, ip:str, port:int, handler: callable = None):
        self.ip = ip
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse address
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting
        self.__socket.bind((self.ip, self.port))
        
        self.handler = handler

    def send(self, data:bytes, ip_remote:str, port_remote:int):
        remote_address = (ip_remote, port_remote)
        self.__socket.sendto(data, remote_address)

    def listen(self):
        return self.__socket.recvfrom(32768) # Size of the struct

    def close(self):
        self.__socket.close()

    def register_handler(self, handler: callable):
        self.handler = Thread(handler)

    def notify(self, message: MessageInfo=None):
        if self.handler:
            self.handler.args = message
            self.handler.start()
            self.handler.join()
            
