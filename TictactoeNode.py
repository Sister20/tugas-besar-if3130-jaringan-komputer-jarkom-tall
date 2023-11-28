from threading import Thread
from Node import Node
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from connection.Connection import Connection
from connection.TCPConnection import TCPConnection
from connection.OncomingConnection import OncomingConnection
from file.ReceiverFile import ReceiverFile

from tictactoe.TicTacToeGame import TicTacToeGame

# Peer to peer
class TictactoeNode(Node):
    def __init__(self, ip: str = '0.0.0.0', port: int = 8081, server_port: int = 8082) -> None:
        super().__init__(TCPConnection(ip, port))
        self.connection: TCPConnection = self.connection
        self.game = TicTacToeGame(self.connection)
        self.ip: str = ip
        self.port: int = port
        self.server_port: int = server_port

    def find_match(self):
        print(f"Finding a match in port {self.server_port}")
        response: OncomingConnection = self.connection.requestHandshake("<broadcast>", self.server_port)
        if (response.valid):
            Terminal.log(f"Connection Established", Terminal.ALERT_SYMBOL, "Handshake")
        else:
            if (response.error_code == OncomingConnection.ERR_TIMEOUT):
                Terminal.log(f"Connection timeout! Shutting down...", Terminal.CRITICAL_SYMBOL, "Error")

        return response

    def wait_match(self):
        print(f"Waiting for a match in port {self.port}")
        request = None
        try:
            request: OncomingConnection = self.connection.acceptHandshake()
            if (request.valid):
                Terminal.log(f"Connection established", Terminal.ALERT_SYMBOL, "Handshake")
            else:
                if request.error_code == OncomingConnection.ERR_TIMEOUT:
                    Terminal.log(f"Connection timeout with {request.address[0]}:{request.address[1]}", Terminal.CRITICAL_SYMBOL)
                if request.error_code == OncomingConnection.ERR_RESET:
                    Terminal.log(f"Connection reset with {request.address[0]}:{request.address[1]}", Terminal.CRITICAL_SYMBOL)
        except TimeoutError as e:
            print("Match not found!")

        return request

    def run(self):
        self.running = True
        self.connection.startListening()
        while self.running:
            user_input = input("Would you like to wait for a match (W), find a match (F), or quit (Q)?: ")
            if(user_input == 'W'): 
                request = self.wait_match()
                if (not request or not request.valid):
                    print("Failed to find a match")
                    print("Resetting...\n\n\n")
                    continue
                
                # The acceptor receives the initiator's selection
                print(request.address[0], request.address[1])

                self.game.set_peer(request)
                self.game.initialize_waiter()
                self.game.summary()

                print("Game is done!")
                print("Resetting...\n\n\n")
                pass
            elif(user_input == 'F'): 
                request = self.find_match()
                if (not request or not request.valid):
                    print("Failed to find a match")
                    print("Resetting...\n\n\n")
                    continue

                # The initiator chooses
                print(request.address[0], request.address[1])
                
                self.game.set_peer(request)
                self.game.initialize_finder()
                self.game.summary()

                print("Game is done!")
                print("Resetting...\n\n\n")
                pass
            elif(user_input == 'Q'):
                # TODO: close the connection properly
                break
            else:
                print("Invalid input!")

        self.stop()

    def stop(self):
        self.running = False
        self.connection.close()

if __name__ == "__main__":
    print("Starting main in tictactoe")
    client = TictactoeNode()
    Thread(target=client.run).start()

    try:
        while client.running:
            pass
    except KeyboardInterrupt:
        Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
        client.stop()
