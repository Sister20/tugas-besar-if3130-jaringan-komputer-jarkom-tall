from threading import Thread
from utils.Node import Node
from utils.MessageInfo import MessageInfo
from utils.Connection import Connection
from utils.Logger import Logger
from utils.Segment import Segment

class Client(Node):
    def __init__(self, ip: str='0.0.0.0', port:int=8082, server_port:int=8080) -> None:
        super().__init__(Connection(ip, port))
        self.__connection:Connection = self._Node__connection
        self.__connection.setTimeout(30) # Default timeout is 30s
        self.ip:str = ip
        self.port:int = port
        self.server_port:int = server_port

    def run(self):
        self.running = True
        try:    
            # Broadcast
            self.__connection.send(
                MessageInfo('<broadcast>', self.server_port,
                             Segment(0, 0, 0, "DISCOVER".encode())
                             ))
            data, server_address = self.__connection.listen()
            data, checksum = Segment.unpack(data)
            string_data = data.payload.decode().strip('\x00')

            Logger.alert(f"Received response from server at {server_address[0]}:{server_address[1]}")
            Logger.alert(f"Response: {data.payload.decode()}")

            # If the server replied, we may establish connection and hence timeout is set for longer
            self.__connection.setTimeout(300)

            # TODO: utilize appropriate protocols and types, file transfer and handshake goes here
            while(string_data != "DONE"):
                data, server_address = self.__connection.listen()
                data, checksum = Segment.unpack(data)
                string_data = data.payload.decode().strip('\x00')
                Logger.alert(f"Response: {string_data}")
                if(string_data == "DONE"):
                    Logger.critical(f"Server finished, stopping")
                    self.stop()
        except TimeoutError:
            print("Connection Timeout!")
            self.stop()
            return

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