from threading import Thread
from Node import Node
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
from connection.TCPConnection import TCPConnection
from connection.OncomingConnection import OncomingConnection
from file.ReceiverFile import ReceiverFile
from message.MessageQuery import MessageQuery


class Client(Node):
    def __init__(self, output_file_path: str, ip: str = '0.0.0.0', port: int = 8083, server_port: int = 8000) -> None:
        super().__init__(TCPConnection(ip, port))
        self.connection: TCPConnection = self.connection
        self.ip: str = ip
        self.port: int = port
        self.server_port: int = server_port
        self.output_file = ReceiverFile(output_file_path)

    def run(self):
        self.connection.startListening()
        self.connection.send(Segment(0, 0, 0, b'DISCOVER').pack(), "<broadcast>", self.server_port)
        discover = self.connection.listen(MessageQuery(payload=b'AVAILABLE'), 30)
        Terminal.log(f"Server found at {discover.ip}:{discover.port}")

        response: OncomingConnection = self.connection.acceptHandshake((discover.ip, discover.port), None)
        if (response.valid):
            Terminal.log(f"Connection Established", Terminal.ALERT_SYMBOL, "Handshake")
            print("Listening")
            response, buffer = self.connection.receiveGoBackN(response)
            for buff in buffer:
                self.output_file.write(buff)
        else:
            if (response.error_code == OncomingConnection.ERR_TIMEOUT):
                Terminal.log(f"Connection timeout! Shutting down...", Terminal.CRITICAL_SYMBOL, "Error")
        print("Done")
        self.stop()

    def stop(self):
        self.running = False
        self.output_file.close()
        self.connection.close()


if __name__ == "__main__":
    print("Starting main in client")
    for i in range(5):
        client = Client(f"Out{i}.png", port=8080 + i)
        Thread(target=client.run).start()

    try:
        while client.running:
            pass
    except KeyboardInterrupt:
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        client.stop()
