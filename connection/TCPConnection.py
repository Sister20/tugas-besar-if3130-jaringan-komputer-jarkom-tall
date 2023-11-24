import socket
import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.Connection import Connection
from connection.OncomingConnection import OncomingConnection
from random import randint

class TCPConnection(Connection):
    def __init__(self, ip:str, port:int, handler: callable = None) -> None:
        super().__init__(ip, port, handler)

    def requestHandshake(self, ip_remote: str, port_remote:int) -> OncomingConnection:
        seq_num = randint(0, 4294967295)

        self.setTimeout(Config.HANDSHAKE_TIMEOUT)
        remote_address = (ip_remote, port_remote)
        Terminal.log("Initiating three way handshake", Terminal.ALERT_SYMBOL)
        try:
            Terminal.log(f"Sending SYN request to {ip_remote}:{port_remote}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(seq_num))
            self.socket.sendto(Segment.syn(seq_num).pack(), remote_address)

            while True:
                Terminal.log("Waiting for response...", Terminal.ALERT_SYMBOL, "Handshake")
                data, client_address = self.listen()
                if(client_address == ip_remote or ip_remote == '<broadcast>'):
                    try:
                        data, checksum = Segment.unpack(data)
                        if data.flags == SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK:
                            Terminal.log(f"Accepted SYN-ACK from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(data.seq_num))
                            
                            ack_num = data.seq_num + 1
                            seq_num = seq_num + 1
                            
                            self.socket.sendto(Segment.ack(seq_num, ack_num).pack(), client_address)
                            Terminal.log(f"Sending ACK to {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(seq_num))
                            
                            self.setTimeout(None)
                            return OncomingConnection(True, client_address, seq_num, ack_num)
                        
                    except Exception as e:
                        print(e)
                        Terminal.log(f"Received bad response from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Error")

        except TimeoutError:
            self.socket.sendto(Segment.rst().pack(), remote_address)
            Terminal.log(f"Handshake timeout", Terminal.CRITICAL_SYMBOL, "Handshake")
            self.setTimeout(None)
            return OncomingConnection(False, (ip_remote, port_remote), 0, 0, OncomingConnection.ERR_TIMEOUT)

    def acceptHandshake(self) -> OncomingConnection:
        seq_num = randint(0, 4294967295)
        
        data, client_address = self.listen()
        try:
            data, checksum = Segment.unpack(data)
        except Exception:
            Terminal.log(f"Received bad request from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Error")
            return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_INVALID_SEGMENT)
        
        if data.flags == SegmentFlag.FLAG_SYN:
            Terminal.log(f"Received SYN from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(data.seq_num))
            
            ack_num = data.seq_num + 1

            self.socket.sendto(Segment.syn_ack(seq_num, ack_num).pack(), client_address)
            Terminal.log(f"Sending SYN-ACK to {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(seq_num))
            
            client = client_address

            self.setTimeout(Config.HANDSHAKE_TIMEOUT)
            try:
                while True:
                    data, client_address = self.listen()
                    while(client_address != client):
                        continue

                    try:
                        data, checksum = Segment.unpack(data)
                    except:
                        Terminal.log(f"Received bad response from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Error")
                        continue

                    if data.flags == SegmentFlag.FLAG_ACK and data.ack_num == seq_num + 1:
                        Terminal.log(f"Received ACK from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake SEQ_NUM=" + str(data.seq_num))
                        
                        self.setTimeout(None)
                        return OncomingConnection(True, client_address, data.seq_num, data.ack_num)
                    
                    if data.flags == SegmentFlag.FLAG_RST:
                        Terminal.log(f"Received RST from {client_address[0]}:{client_address[1]}", Terminal.CRITICAL_SYMBOL, "Handshake")
                        
                        self.setTimeout(None)
                        return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_RESET)

            except TimeoutError:
                Terminal.log(f"No ACK received from {client[0]}:{client[1]}", Terminal.CRITICAL_SYMBOL, "Handshake")
                
                self.setTimeout(None)
                return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_TIMEOUT)
    