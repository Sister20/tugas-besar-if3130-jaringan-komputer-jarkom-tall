from utils.Terminal import Terminal

class ReceiverFile:
    def __init__(self, path: str) -> None:
        self.path = path
        self.file = self.__create()

    def __create(self) -> None:
        try:
            return open(self.path, 'wb')
        except FileNotFoundError:
            Terminal.log(f'File not found: {self.path}')
            Terminal.log('Exiting program...')
            exit(1)

    def write(self, payload: bytes) -> None:
        self.file.write(payload)

    def close(self) -> None:
        self.file.close()
