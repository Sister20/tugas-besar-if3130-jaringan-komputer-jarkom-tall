from connection.Connection import Connection
from message.Segment import Segment

# Supposed to be an abstract class, python does not have it though
# Just don't use it
class Node:
    def __init__(self, connection:Connection):
        self.__connection = connection
        self.running = False

    def run(self):
        raise NotImplementedError("Node is an abstract class")

    def stop(self):
        raise NotImplementedError("Node is an abstract class")

    def handle_message(self, segment: Segment):
        raise NotImplementedError("Node is an abstract class")