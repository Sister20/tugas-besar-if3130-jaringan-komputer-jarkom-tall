from threading import Thread
from utils.Node import Node
from utils.Connection import Connection
from utils.Logger import Logger
from utils.Segment import Segment

class Server(Node):
    def __init__(self, served_filepath:str, ip: str='0.0.0.0', port:int=8080) -> None:
        super().__init__(Connection(ip, port))
        self.__connection:Connection = self._Node__connection
        self.ip:str = ip
        self.port:int = port
        self.served_filepath:str = served_filepath
        self.client_list = []

    def __event_loop(self):
        while self.running:
            data, client_address = self.__connection.listen()
            Logger.alert(f"Received connection from {client_address[0]}/{client_address[1]}")
            self.client_list.append(client_address)
            self.__connection.send("OFFER".encode(), client_address[0], client_address[1])

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
                        self.__connection.send('HANDSHAKE'.encode(), client[0], client[1])
                        
                        #TODO: utilize appropriate protocols and types, file sending goes here
                        self.__connection.send('DONE'.encode(), client[0], client[1])

                    Logger.critical("Server finished sending files. Stopping")
                    self.stop()
                    break
                elif accept == 'y':
                    break
                else:
                    Logger.alert("Invalid input!")


    def run(self):
        self.running = True
        Logger.alert(f"Server started at {self.ip}:{self.port}")
        Thread(target=self.__event_loop).start()

    def stop(self):
        self.running = False
        self.__connection.close()

    def handle_message(self, segment: Segment):
        # TODO: Implement
        pass

if __name__ == "__main__":
    print("Starting main in server")
    server = Server("Test.txt")
    server.run()

    try:
        while server.running:
            pass
    except KeyboardInterrupt:
        Logger.critical("Keyboard interrupt received. Stopping")
        server.stop()