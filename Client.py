import socket
import threading
from utils.Logger import Logger

class Client:
    def __init__(self, server_port:int=8080, default_buffer_size:int=1024):
        self.server_port = server_port
        self.broadcast_address = ('<broadcast>', self.server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.running = False
        self.default_buffer_size = default_buffer_size

    def run(self):
        self.running = True

        # TODO: utilize appropriate protocols and types, handshake goes here
        self.send_broadcast("DISCOVER")
        local_address, local_port = self.socket.getsockname()
        Logger.alert(f"Client started. Local address: {local_address}, Local port: {local_port}")
        
        response, server_address = self.receive_data()
        self.server_address = server_address

        Logger.alert(f"Received response from server at {self.server_address[0]}:{self.server_address[1]}")
        Logger.alert(f"{response.decode()}")

        # TODO: utilize appropriate protocols and types, file transfer goes here
        response, server_address = self.receive_data()
        if(response.decode() == "DONE"):
            Logger.critical(f"Server finished, stopping")
            self.stop()

    # TODO: utilize appropriate protocols and types
    def send_broadcast(self, message:str):
        self.socket.sendto(message.encode(), self.broadcast_address)
    
    # TODO: utilize appropriate protocols and types
    def send_data(self, message:str):
        self.socket.sendto(message.encode(), self.server_address)

    # TODO: utilize appropriate protocols and types
    def receive_data(self):
        return self.socket.recvfrom(self.default_buffer_size)

    def stop(self):
        self.running = False
        self.socket.close()

if __name__ == "__main__":
    client = Client(8080)
    threading.Thread(target=client.run).start()

    try:
        while client.running:
            pass
    except KeyboardInterrupt:
        Logger.critical("Keyboard interrupt received. Stopping")
        client.stop()