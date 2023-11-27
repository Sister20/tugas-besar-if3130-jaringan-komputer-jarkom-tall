# Constants
HANDSHAKE_TIMEOUT = 10  # Time for nodes to receive the proper response during a handshake
CLIENT_TIMEOUT = 20  # Time for client to find a server

RESPONSE_TIMEOUT = 4
SEND_RETRIES = 5
RETRANSMIT_TIMEOUT = 15

SEGMENT_SIZE = 32768
PAYLOAD_SIZE = 32756        # From SEGMENT_SIZE - header size (12 bytes)
