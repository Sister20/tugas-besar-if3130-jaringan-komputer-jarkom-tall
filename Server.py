from threading import Thread
from utils.Terminal import Terminal
from Node import Node
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
from connection.TCPConnection import TCPConnection
from connection.OncomingConnection import OncomingConnection

class Server(Node):
    def __init__(self, served_filepath:str, ip: str='0.0.0.0', port:int=8000) -> None:
        super().__init__(TCPConnection(ip, port))
        self.__connection:TCPConnection = self._Node__connection
        self.__connection.setTimeout(None)
        self.ip:str = ip
        self.port:int = port
        self.served_filepath:str = served_filepath
        self.client_list = []

    def __event_loop(self):
        while self.running:
            request: OncomingConnection =  self.__connection.acceptHandshake()

            if(request.valid):
                Terminal.log(f"Connection established", Terminal.ALERT_SYMBOL, "Handshake")
            else:
                if request.error_code == OncomingConnection.ERR_TIMEOUT:
                    Terminal.log(f"Connection timeout with {request.address[0]}:{request.address[1]}", Terminal.CRITICAL_SYMBOL)
                if request.error_code == OncomingConnection.ERR_RESET:
                    Terminal.log(f"Connection reset with {request.address[0]}:{request.address[1]}", Terminal.CRITICAL_SYMBOL)

    def run(self):
        self.running = True
        Terminal.log(f"Server started at {self.ip}:{self.port}", Terminal.ALERT_SYMBOL)
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
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        server.stop()