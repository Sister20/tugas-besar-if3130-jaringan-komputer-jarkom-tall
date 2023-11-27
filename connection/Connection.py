import socket
import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.OncomingConnection import OncomingConnection
from random import randint


class Connection:
    def __init__(self, ip: str, port: int, handler: callable = None) -> None:
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        self.socket.bind((self.ip, self.port))

        self.handler = handler

    def send(self, data: bytes, ip_remote: str, port_remote: int) -> None:
        # if (randint(1, 10) > 4):
        #     print("Packet loss!!!")
        #     return
        remote_address = (ip_remote, port_remote)
        self.socket.sendto(data, remote_address)

    def listen(self):
        return self.socket.recvfrom(32768)

    def close(self) -> None:
        self.socket.close()

    def register_handler(self, handler: callable) -> None:
        self.handler = Thread(handler)

    def notify(self, message: MessageInfo = None):
        if self.handler:
            self.handler.args = message
            self.handler.start()
            self.handler.join()

    def setTimeout(self, time_seconds: float) -> None:
        # NOTE: use None to set for no timeouts
        self.socket.settimeout(time_seconds)
