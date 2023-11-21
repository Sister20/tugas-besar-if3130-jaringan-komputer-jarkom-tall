from threading import Thread
from utils.Node import Node
from utils.MessageInfo import MessageInfo
from utils.Connection import Connection, OncomingConnection
from utils.Logger import Logger
from utils.Segment import Segment

class Server(Node):
    def __init__(self, served_filepath:str, ip: str='0.0.0.0', port:int=8000) -> None:
        super().__init__(Connection(ip, port))
        self.__connection:Connection = self._Node__connection
        self.__connection.setTimeout(None)
        self.ip:str = ip
        self.port:int = port
        self.served_filepath:str = served_filepath
        self.client_list = []

    def __event_loop(self):
        while self.running:
            request: OncomingConnection =  self.__connection.open()

            if(request.valid):
                data, client_address = self.__connection.listen()
                Logger.log(f"Received data from {client_address[0]}:{client_address[1]}", Logger.ALERT_SYMBOL)
                Logger.log(f"Data is {data.decode()}")
            else:
                if request.error_code == OncomingConnection.ERR_TIMEOUT:
                    Logger.log(f"Connection timeout with {request.address[0]}:{request.address[1]}", Logger.CRITICAL_SYMBOL)
                if request.error_code == OncomingConnection.ERR_RESET:
                    Logger.log(f"Connection reset with {request.address[0]}:{request.address[1]}", Logger.CRITICAL_SYMBOL)

    def run(self):
        self.running = True
        Logger.log(f"Server started at {self.ip}:{self.port}", Logger.ALERT_SYMBOL)
        Thread(target=self.__event_loop).start()

    def stop(self):
        self.running = False
        self.__connection.close()

    def handle_message(self, segment: Segment):
        # TODO: Implement
        pass

if __name__ == "__main__":
    print("Starting main in server")
    server = Server("Test.txt")
    server.run()

    try:
        while server.running:
            pass
    except KeyboardInterrupt:
        Logger.log("Keyboard interrupt received. Stopping", Logger.CRITICAL_SYMBOL)
        server.stop()