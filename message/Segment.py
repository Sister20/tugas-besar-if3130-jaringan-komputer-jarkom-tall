import struct
from message.SegmentFlag import SegmentFlag


class Segment():
    def __init__(self, flags: int, seq_num: int, ack_num: int, payload: bytes):
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

    @staticmethod
    def syn(seq_num: int):
        return Segment(SegmentFlag.FLAG_SYN, seq_num, 0, "".encode())

    @staticmethod
    def ack(seq_num: int, ack_num: int):
        return Segment(SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def syn_ack(seq_num: int, ack_num: int):
        return Segment(SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def fin(seq_num: int):
        return Segment(SegmentFlag.FLAG_FIN, seq_num, 0, "".encode())

    @staticmethod
    def fin_ack(seq_num: int, ack_num: int):
        return Segment(SegmentFlag.FLAG_FIN | SegmentFlag.FLAG_ACK, seq_num, ack_num, "".encode())

    @staticmethod
    def rst():
        return Segment(SegmentFlag.FLAG_RST, 0, 0, "".encode())

    def __calculate_checksum(self):
        # mengubah data segment menjadi data biner
        data = struct.pack(">IIBBH32756s",
                           self.seq_num,
                           self.ack_num,
                           self.flags,
                           self.reserved,
                           0,
                           self.payload
                           )
        # mengubah nilai checksum menjadi 0
        # data = data[:10] + b'\x00\x00' + data[12:]
        # mengubah data menjadi daftar bilangan bulat 16 bit
        words = struct.unpack("!%dH" % (len(data) // 2), data)
        # menjumlahkan semua kata dengan memperhatikan carry
        sum = 0
        for word in words:
            sum += word
            if sum > 0xffff:
                sum = (sum & 0xffff) + 1

        # mengambil satu komplement dari hasil penjumlahan
        return ~sum & 0xffff

    def update_checksum(self):
        self.checksum = self.__calculate_checksum()

    def is_valid_checksum(self):
        return self.__calculate_checksum() == self.checksum
