import struct

class SegmentFlag():
    # ini gimana caranya bikin enum/static di python anjir
    FLAG_NONE = 0
    FLAG_FIN = 1
    FLAG_SYN = 2
    FLAG_ACK = 16