from utils.Terminal import Terminal
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from typing import List
import os, math
from Config import PAYLOAD_SIZE

class SenderFile:
    dummy_ack_num = 0
    dummy_seq_num = 0

    def __init__(self, path: str) -> None:
        self.path = path
        self.file = self.__open()
        self.size = self.__get_size()
        self.chunk_count = self.__get_chunk_count()
        self.segments = self.__get_base_segments()

    def __open(self) -> None:
        try:
            return open(self.path, 'rb')
        except FileNotFoundError:
            Terminal.log(f'File not found: {self.path}')
            Terminal.log('Exiting program...')
            exit(1)

    def __get_size(self) -> int:
        try:
            return os.path.getsize(self.path)
        except FileNotFoundError:
            Terminal.log(f'File not found: {self.path}')
            Terminal.log('Exiting program...')
            exit(1)

    def __get_chunk_count(self) -> int:
        return math.ceil(self.size / PAYLOAD_SIZE)

    def __get_chunk(self, idx: int) -> bytes:
        # Optimize using seek with offset idx * PAYLOAD_SIZE
        self.file.seek(idx * PAYLOAD_SIZE)
        return self.file.read(PAYLOAD_SIZE)

    def __get_base_segments(self) -> List[Segment]:
        segments: List[Segment] = []

        for i in range(self.chunk_count):
            segment = Segment(SegmentFlag.FLAG_NONE, SenderFile.dummy_seq_num, SenderFile.dummy_ack_num, self.__get_chunk(i))
            segments.append(segment)

        return segments

    def set_seq_num(self, handshake_seq_num: int, handshake_ack_num: int) -> None:
        for i in range(self.chunk_count):
            # Ex:
            # Handshake: seq num SYN => 0, seq num ACK => 1
            # First payload (idx 0) will be sent with seq num 1 + 0 + 1 = 2
            self.segments[i].seq_num = handshake_seq_num + i
            self.segments[i].ack_num = handshake_ack_num + i

    def close(self) -> None:
        self.file.close()
