from utils.Terminal import Terminal
from TictactoeNode import TictactoeNode
from threading import Thread

print("Starting tictactoe")
client = TictactoeNode('0.0.0.0', 8081, 8082)
Thread(target=client.run).start()

try:
    while client.running:
        pass
except KeyboardInterrupt:
    Terminal.log("Keyboard interrupt received. Stopping", Terminal.CRITICAL_SYMBOL)
    client.stop()
