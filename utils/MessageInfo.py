from utils.Segment import Segment

class MessageInfo:
    def __init__(self, ip:str, port:int, segment:Segment):
        self.ip = ip
        self.port = port
        self.segment = segment