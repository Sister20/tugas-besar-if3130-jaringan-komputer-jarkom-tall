class OncomingConnection:
    ERR_TIMEOUT = 1
    ERR_INVALID_SEGMENT = 2
    ERR_RESET = 4

    def __init__(self, valid: int, address: any, seq_num: int, ack_num: int, error_code: int = 0) -> None:
        self.valid = valid
        self.address = address
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.error_code = error_code
