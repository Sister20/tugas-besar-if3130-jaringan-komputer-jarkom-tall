import socket
import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.MessageQuery import MessageQuery
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.OncomingConnection import OncomingConnection
from random import randint
import time
import struct

class Connection:
    def __init__(self, ip: str, port: int, handler: callable = None) -> None:
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        self.socket.settimeout(None)
        self.socket.bind((self.ip, self.port))
        self.default_timeout = 30

        self.connection_buffer: list[MessageInfo] = []
        self.handler: callable = handler
        self.listening: bool = False
        self.listener: Thread = Thread(target=self.listenerThread)
        self.garbage_collector: Thread = Thread(target=self.garbageThread)

    def garbageThread(self):
        while self.listening:
            try:
                initial_package = self.connection_buffer[0]
                
                time.sleep(Config.GARBAGE_COLLECTION_TIME)

                if(initial_package == self.connection_buffer[0]):
                    print("Garbage collected")
                    self.connection_buffer.pop(0)
            except IndexError as e:
                pass

    def listenerThread(self):
        while self.listening:
            data, client_address = self.socket.recvfrom(32768)
            try:
                message = MessageInfo(ip = client_address[0], port = client_address[1], segment = Segment.unpack(data)[0])
                message.segment.payload = message.segment.payload.strip(b'\x00')
                if(not message.segment.is_valid_checksum()): raise struct.error

                self.connection_buffer.append(message)
                if(self.handler): self.handler()
            except struct.error:
                print("bad packet")
                pass

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

    def listen(self, query: MessageQuery = None, timeout: int = None) -> MessageInfo:
        retval = None
        if(timeout):
            start_time = time.time()
            limit = start_time + timeout
        
        if(query is None):
            while retval is None:
                try:
                    retval = self.connection_buffer.pop(0)
                except IndexError:
                    pass
                if (timeout and time.time() > limit): raise TimeoutError()
        else:
            while retval is None:
                try:
                    if(query.validate(self.connection_buffer[0])):
                        retval = self.connection_buffer.pop(0)
                except IndexError:
                    pass
                if (timeout and time.time() > limit): raise TimeoutError()

        return retval
        # return self.socket.recvfrom(32768)

    def close(self) -> None:
        try:
            self.socket.close()
        finally:
            self.stopListening()
