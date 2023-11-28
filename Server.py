from threading import Thread
from utils.Terminal import Terminal
from Node import Node
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
from connection.TCPConnection import TCPConnection
# from testing.TCPConnection2 import TCPConnection
from connection.OncomingConnection import OncomingConnection
from file.SenderFile import SenderFile
from file.ReceiverFile import ReceiverFile


class Server(Node):
    def __init__(self, served_filepath: str, ip: str = '0.0.0.0', port: int = 8000) -> None:
        super().__init__(TCPConnection(ip, port))
        self.connection: TCPConnection = self.connection
        self.connection.setTimeout(None)
        self.ip:str = ip
        self.port:int = port
        self.file = SenderFile(served_filepath)
        self.client_list = []
        self.sending = False

    def send_file(self, connection):
        self.file.set_num(connection.seq_num, connection.ack_num)
        print(connection.seq_num)
        self.connection.sendGoBackN(self.file.segments, connection.address[0], connection.address[1])

    def __event_loop(self):
        while self.running:
            data, client_addr = self.connection.listen()
            self.connection.send("AVAILABLE".encode(), client_addr[0], client_addr[1])

            self.client_list.append(client_addr)
            Terminal.log(f"Connection made with {client_addr[0]}:{client_addr[1]}")
            self.connection.setTimeout(None)
            
            userInput = Terminal.input("Listen for more? (y/N)")
            

            if(userInput != "N"):
                continue
            
            print(self.client_list)
            for client_address in self.client_list:
                connection: OncomingConnection = self.connection.requestHandshake(client_address[0], client_address[1])
                if (connection != None and connection.valid):
                    Terminal.log(f"Connection established with {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake")
                    self.send_file(connection)
                    # Thread(target=self.send_file, args=[connection]).start()
                else:
                    Terminal.log(f"Failed to establish connection with {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake")
            self.client_list.clear()

    def run(self):
        self.running = True
        Terminal.log(f"Server started at {self.ip}:{self.port}", Terminal.ALERT_SYMBOL)
        Thread(target=self.__event_loop).start()

    def stop(self):
        self.running = False
        self.file.close()
        self.connection.close()

    def handle_message(self, segment: Segment):
        # TODO: Implement
        pass


if __name__ == "__main__":
    print("Starting main in server")
    server = Server("test.png")
    server.run()

    try:
        while server.running:
            pass
    except KeyboardInterrupt:
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        server.stop()
