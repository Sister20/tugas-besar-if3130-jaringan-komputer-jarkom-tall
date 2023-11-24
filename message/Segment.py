import struct
from message.SegmentFlag import SegmentFlag

class Segment():
    # ini gimana caranya bikin struct di python anjir
    def __init__(self, flags:int, seq_num:int, ack_num:int, payload:bytes):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.reserved = 0
        self.payload = payload
        self.checksum = self.__calculate_checksum()

    
    def pack(self):
        return struct.pack(">IIBBH32756s",
                           self.seq_num,
                           self.ack_num,
                           self.flags,
                           self.reserved,
                           self.checksum,
                           self.payload
                           )
    
    @classmethod
    def unpack(cls, packed_data):
        unpacked_data = struct.unpack('>IIBBH32756s', packed_data)
        seq_num, ack_num, flags, reserved, checksum, payload = unpacked_data
        return cls(flags, seq_num, ack_num, payload), checksum
    
    @classmethod
    def unpack_str_payload(cls, packed_data):
        unpacked_data = struct.unpack('>IIBBH32756s', packed_data)
        seq_num, ack_num, flags, reserved, checksum, payload = unpacked_data
        return cls(flags, seq_num, ack_num, payload.decode().strip('\x00')), checksum


    @staticmethod
    def syn(seq_num:int):
        return Segment(SegmentFlag.FLAG_SYN, seq_num, 0, "".encode())
    
    @staticmethod
    def ack(seq_num:int, ack_num:int):
        return Segment(SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def syn_ack(seq_num:int, ack_num:int):
        return Segment(SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def fin(seq_num:int):
        return Segment(SegmentFlag.FLAG_FIN, seq_num, 0, None)
    
    @staticmethod
    def fin_ack(seq_num:int, ack_num:int):
        return Segment(SegmentFlag.FLAG_FIN | SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def rst():
        return Segment(SegmentFlag.FLAG_RST, 0, 0, "".encode())

    def __calculate_checksum(self):
        # TODO: implement
        return 0
    
    def update_checksum(self):
        # TODO: implement
        return 0
    
    def is_valid_checksum(self):
        # TODO: implement
        return True
    
