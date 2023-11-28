import socket

server_ip = "0.0.0.0"
server_port = 12345  # Use the same port number as in the client

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific address and port
udp_socket.bind((server_ip, server_port))

print(f"UDP server listening on {server_ip}:{server_port}")

while True:
    # Receive data from the client
    data, client_address = udp_socket.recvfrom(1024)
    print(f"Received data from {client_address}: {data.decode()}")