from threading import Thread
from utils.Node import Node
from utils.MessageInfo import MessageInfo
from utils.Connection import Connection, OncomingConnection
from utils.Terminal import Terminal
from utils.Segment import Segment

class Client(Node):
    def __init__(self, ip: str='0.0.0.0', port:int=8082, server_port:int=8000) -> None:
        super().__init__(Connection(ip, port))
        self.__connection:Connection = self._Node__connection
        self.__connection.setTimeout(30) # Default timeout is 30s
        self.ip:str = ip
        self.port:int = port
        self.server_port:int = server_port

    def run(self):
        self.running = True
        # while True:
        response: OncomingConnection = self.__connection.send("Testing".encode(), "<broadcast>", self.server_port)
        if(response.valid):
            Terminal.log(f"Done", Terminal.ALERT_SYMBOL, "Handshake")
        else:
            if(response.error_code == OncomingConnection.ERR_TIMEOUT):
                Terminal.log(f"Connection timeout! Shutting down...", Terminal.CRITICAL_SYMBOL, "Error")
        self.stop()
        # break

    def stop(self):
        self.running = False
        self.__connection.close()

    def handle_message(self, segment: Segment):
        # TODO: Implement
        pass

if __name__ == "__main__":
    print("Starting main in client")
    client = Client()
    Thread(target=client.run).start()

    try:
        while client.running:
            pass
    except KeyboardInterrupt:
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        client.stop()