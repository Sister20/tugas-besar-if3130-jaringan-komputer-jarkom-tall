import socket
import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.OncomingConnection import OncomingConnection
from random import randint
import time

class Connection:
    def __init__(self, ip: str, port: int, handler: callable = None) -> None:
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        self.socket.bind((self.ip, self.port))

        self.connection_buffer = []
        self.handler = handler
        self.listening = True
        self.listener = Thread(target=self.listenerThread)
        self.garbage_collector = Thread(target=self.garbageThread)

    def garbageThread(self):
        while self.listening:
            if(len(self.connection_buffer) > 0):
                initial_package = self.connection_buffer[0]
                
                time.sleep(Config.GARBAGE_COLLECTION_TIME)

                if(len(self.connection_buffer) > 0):
                    if(initial_package == self.connection_buffer[0]):
                        self.connection_buffer.pop(0)




    def listenerThread(self):
        while self.listening:
            self.connection_buffer.append(self.socket.recvfrom(32768))
            if(self.handler): self.handler()

    def stopListening(self):
        self.listening = False
        self.listener.join()
        self.listener = Thread(target=self.listenerThread)
        self.garbage_collector = Thread(target=self.garbageThread)
    
    def startListening(self):
        self.listening = True
        self.listener.start()
        self.garbage_collector.start()

    def send(self, data: bytes, ip_remote: str, port_remote: int) -> None:
        # if (randint(1, 10) == 1):
        #     print("Packet loss!!!")
        #     return
        remote_address = (ip_remote, port_remote)
        self.socket.sendto(data, remote_address)

    def listen(self, message: MessageInfo = None, timeout: int = None):
        retval = None
        if(timeout):
            start_time = time.time()
            limit = start_time + timeout
        
        if(message is None):
            while retval is None:
                try:
                    retval = self.connection_buffer.pop(0)
                except IndexError:
                    pass
                if (timeout and time.time() > limit): raise TimeoutError()
        else:
            while retval is None:
                try:
                    if(len(self.connection_buffer) != 0 and self.connection_buffer[0] == message):
                        retval = self.connection_buffer.pop(0)
                except IndexError:
                    pass
                if (timeout and time.time() > limit): raise TimeoutError()

        return retval
        # return self.socket.recvfrom(32768)

    def close(self) -> None:
        self.stopListening()
        self.socket.close()

    def setTimeout(self, time_seconds: float) -> None:
        # NOTE: use None to set for no timeouts
        self.socket.settimeout(time_seconds)
