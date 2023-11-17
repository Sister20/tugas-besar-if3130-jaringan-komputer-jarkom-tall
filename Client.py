from threading import Thread
from utils.Node import Node
from utils.Connection import Connection
from utils.Logger import Logger
from utils.Segment import Segment

class Client(Node):
    def __init__(self, ip: str='0.0.0.0', port:int=8081, server_port:int=8080) -> None:
        super().__init__(Connection(ip, port))
        self.__connection:Connection = self._Node__connection
        self.ip:str = ip
        self.port:int = port
        self.server_port:int = server_port

    def run(self):
        self.running = True
        
        # Broadcast
        self.__connection.send("test".encode(), '<broadcast>', self.server_port)
        data, server_address = self.__connection.listen()
        Logger.alert(f"Received response from server at {server_address[0]}:{server_address[1]}")
        Logger.alert(f"Response: {data.decode()}")

        # TODO: utilize appropriate protocols and types, file transfer and handshake goes here
        while(data.decode() != "DONE"):
            data, server_address = self.__connection.listen()
            Logger.alert(f"Response: {data.decode()}")
            if(data.decode() == "DONE"):
                Logger.critical(f"Server finished, stopping")
                self.stop()

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
        Logger.critical("Keyboard interrupt received. Stopping")
        client.stop()