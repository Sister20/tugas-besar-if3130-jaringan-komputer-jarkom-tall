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
import os
import argparse

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
        connection = self.connection.sendGoBackN(file.segments, ip, port)
        connection = self.connection.requestTeardown(ip, port, connection.seq_num + 1)
        connection = self.connection.acceptTeardown(connection.seq_num)

    def __event_loop(self):
        self.connection.startListening()
        while self.running:
            userInput = Terminal.input("Do you want to serve file (S), get file (G) or Quit (Q)?")
            if(userInput == "S"):
                filename = Terminal.input("Enter filename: ")
                if not os.path.isfile(filename):
                    print("File not found!")
                    continue

                self.served_file_path = filename
                serve_file = True
                while serve_file:
                    discover = self.connection.listen(MessageQuery(payload=b'DISCOVER'))
                    Terminal.log(f"Connection made with {discover.ip}:{discover.port}")
                    self.connection.send(Segment(0, 0, 0, b'AVAILABLE').pack(), discover.ip, discover.port)

                    self.client_list.append((discover.ip, discover.port))
                    userInput = Terminal.input("Listen for more? (y/N)")

                    if(userInput != "N"):
                        continue
                    
                    threads = []
                    print(self.client_list)
                    for client_address in self.client_list:
                        connection: OncomingConnection = self.connection.requestHandshake(client_address[0], client_address[1])
                        if (connection != None and connection.valid):
                            Terminal.log(f"Connection established with {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake")
                            thread = Thread(target=self.send_file, args=[connection])
                            threads.append(thread)
                            thread.start()
                        else:
                            Terminal.log(f"Failed to establish connection with {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, "Handshake")
                    self.client_list.clear()
                    threads.clear()

                    for thread in threads:
                        thread.join()

                    serve_file = False

            elif(userInput == "G"):
                while True:
                    output_file_path = Terminal.input("Enter filepath: ")
                    if os.path.isfile(output_file_path):
                        print("File already exists!")
                        continue

                    self.output_file = ReceiverFile(output_file_path)
                    try:
                        server_port = int(Terminal.input("Enter server port: "))
                        self.server_port = server_port
                        break
                    except:
                        print("Invalid input!")
                        pass
                
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
                    connection: OncomingConnection = self.connection.acceptTeardown(response.seq_num)
                    connection: OncomingConnection = self.connection.requestTeardown(connection.address[0], connection.address[1], connection.seq_num)
                else:
                    if (response.error_code == OncomingConnection.ERR_TIMEOUT):
                        Terminal.log(f"Connection timeout! Shutting down...", Terminal.CRITICAL_SYMBOL, "Error")
                print("Done")

            elif(userInput == "Q"):
                print("Quitting")
                self.stop()
                exit(0)

    def run(self):
        self.running = True
        Terminal.log(f"Application started at {self.ip}:{self.port}", Terminal.ALERT_SYMBOL)
        Thread(target=self.__event_loop).start()

    def stop(self):
        self.running = False
        if(self.file is not None): self.file.close()
        if(self.output_file is not None): self.output_file.close()
        self.connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('port', type=int, default="", help='Application port')
    args = parser.parse_args()

    print("Starting main")
    server = Server("test.png", port=args.port)
    server.run()

    try:
        while server.running:
            pass
    except KeyboardInterrupt:
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        server.stop()
