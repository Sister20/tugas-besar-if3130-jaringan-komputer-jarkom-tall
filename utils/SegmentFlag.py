import struct

class SegmentFlag():
    # ini gimana caranya bikin enum/static di python anjir
    FLAG_NONE = 0
    FLAG_FIN = 1
    FLAG_SYN = 2
    FLAG_ACK = 16

    def __init__(self, value):
        if not 0 <= value <= 255:
            raise ValueError("Value must be an 8-bit integer")
        self.value = value

    def get_flag_bytes(self) -> bytes:
        return struct.pack('B', self.value)