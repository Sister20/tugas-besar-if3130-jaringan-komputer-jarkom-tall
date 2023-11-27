from utils.Terminal import Terminal

class ReceiverFile:
    def __init__(self, path) -> None:
        self.path = path
        self.file = self.__create()

    def __create(self):
        try:
            return open(self.path, 'wb')
        except FileNotFoundError:
            Terminal.log(f'File not found: {self.path}')
            Terminal.log('Exiting program...')
            exit(1)

    def write(self, payload):
        self.file.write(payload)

    def close(self):
        self.file.close()
