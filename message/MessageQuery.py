from message.Segment import Segment
from message.MessageInfo import MessageInfo

class MessageQuery:
    def __init__(self, ip: str = None, port: int = None, flags: int = None, seq_num: int = None, ack_num: int = None, payload: bytes = None):
        self.ip = ip
        self.port = port
        self.flags = flags
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.payload = payload
    
    def validate(self, message: MessageInfo):
        if(self.ip is not None):
            if(message.ip != self.ip):
                return False
        if(self.port is not None):
            if(message.port != self.port):
                return False
        if(self.flags is not None):
            if(message.flags != self.flags):
                return False
        if(self.seq_num is not None):
            if(message.seq_num != self.seq_num):
                return False
        if(self.ack_num is not None):
            if(message.ack_num != self.ack_num):
                return False
        if(self.payload is not None):
            if(message.payload != self.payload):
                return False
            
        return True