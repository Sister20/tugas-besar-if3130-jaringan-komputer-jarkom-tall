from threading import Thread
from Node import Node
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
# from connection.TCPConnection import TCPConnection
from testing.TCPConnection2 import TCPConnection
from connection.OncomingConnection import OncomingConnection

class Client(Node):
    def __init__(self, ip: str='0.0.0.0', port:int=8082, server_port:int=8000) -> None:
        super().__init__(TCPConnection(ip, port))
        self.connection: TCPConnection = self.connection
        self.connection.setTimeout(30) # Default timeout is 30s
        self.ip:str = ip
        self.port:int = port
        self.server_port:int = server_port

    def run(self):
        self.running = True
        response: OncomingConnection = self.connection.requestHandshake("<broadcast>", self.server_port)
        if(response.valid):
            Terminal.log(f"Connection Established", Terminal.ALERT_SYMBOL, "Handshake")
        else:
            if(response.error_code == OncomingConnection.ERR_TIMEOUT):
                Terminal.log(f"Connection timeout! Shutting down...", Terminal.CRITICAL_SYMBOL, "Error")
        self.stop()

    def stop(self):
        self.running = False
        self.connection.close()

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