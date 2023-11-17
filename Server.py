import socket
import threading
from utils.Logger import Logger

class Server:
    def __init__(self, served_filepath:str, address:str='0.0.0.0', port:int=8080):
        super().__init__()
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind((self.address, self.port))
        self.served_filepath = served_filepath
        self.client_list = []

    def server_loop(self):
        while self.running:

            data, client_address = self.socket.recvfrom(1024)
            self.client_list.append(client_address)
            Logger.alert(f"Received request from {client_address[0]}:{client_address[1]}, data: {data.decode()}")
            self.socket.sendto('OFFER'.encode(), client_address)
            
            continue_input = ''
            while not continue_input in ['y', 'n']:
                accept = Logger.input("Listen more? (y/n)")
                if accept == 'n':
                    print("\nClient list:")
                    for i, client in enumerate(self.client_list):
                        print(f"{i + 1}. {client[0]}:{client[1]}")
                    
                    print("")
                    for client in self.client_list:
                        #TODO: utilize appropriate protocols and types, handshake goes here
                        self.socket.sendto('HANDSHAKE'.encode(), client)
                        
                        #TODO: utilize appropriate protocols and types, file sending goes here
                        self.socket.sendto('DONE'.encode(), client)

                    Logger.critical("Server finished sending files. Stopping")
                    self.stop()
                    break
                elif accept == 'y':
                    break
                else:
                    Logger.alert("Invalid input!")

    def run(self):
        self.running = True
        Logger.alert(f"Server started at {self.address}:{self.port}")
        threading.Thread(target=self.server_loop).start()

    def stop(self):
        self.running = False
        self.socket.close()

if __name__ == "__main__":
    server = Server("test.txt", '0.0.0.0', 8080)
    server.run()

    try:
        while server.running:
            pass
    except KeyboardInterrupt:
        Logger.critical("Keyboard interrupt received. Stopping")
        server.stop()