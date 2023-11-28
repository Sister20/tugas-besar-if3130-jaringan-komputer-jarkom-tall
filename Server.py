from threading import Thread
from utils.Terminal import Terminal
from Node import Node
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
from connection.TCPConnection import TCPConnection
from connection.OncomingConnection import OncomingConnection
from file.SenderFile import SenderFile
from file.ReceiverFile import ReceiverFile
from message.MessageQuery import MessageQuery


class Server(Node):
    def __init__(self, served_filepath: str, ip: str = '0.0.0.0', port: int = 8000) -> None:
        super().__init__(TCPConnection(ip, port))
        self.connection: TCPConnection = self.connection
        self.ip:str = ip
        self.port:int = port
        self.served_file_path = served_filepath
        self.client_list = []
        self.sending = False

    def send_file(self, connection: OncomingConnection):
        seq_num=connection.seq_num
        ack_num=connection.ack_num
        ip=connection.address[0]
        port = connection.address[1]
        print("Sending file with connection: ", seq_num, ack_num)
        file: SenderFile = SenderFile(self.served_file_path)
        file.set_num(connection.seq_num, ack_num)
        self.connection.sendGoBackN(file.segments, ip, port)

    def __event_loop(self):
        self.connection.startListening()
        while self.running:
            discover = self.connection.listen(MessageQuery(payload=b'DISCOVER'))
            self.connection.send(Segment(0, 0, 0, b'AVAILABLE').pack(), discover.ip, discover.port)

            self.client_list.append((discover.ip, discover.port))
            Terminal.log(f"Connection made with {discover.ip}:{discover.port}")
            
            userInput = Terminal.input("Listen for more? (y/N)")
            

            if(userInput != "N"):
                continue
            
            print(self.client_list)
            for client_address in self.client_list:
                connection: OncomingConnection = self.connection.requestHandshake(client_address[0], client_address[1])
                if (connection != None and connection.valid):
                    Terminal.log(f"Connection established with {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake")
                    Thread(target=self.send_file, args=[connection]).start()
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
