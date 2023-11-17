import socket
from threading import Thread
from utils.MessageInfo import MessageInfo
from utils.Segment import Segment

class Connection:
    def __init__(self, ip:str, port:int, handler: callable = None):
        self.ip = ip
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse address
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting
        self.__socket.bind((self.ip, self.port))
        
        self.handler = handler

    def send(self, message:MessageInfo):
        remote_address = (message.ip, message.port)
        self.__socket.sendto(message.segment.pack(), remote_address)

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

    def setTimeout(self, time_seconds:int):
        self.__socket.settimeout(time_seconds)

