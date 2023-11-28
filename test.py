import socket

broadcast_ip = "10.8.0.255"
broadcast_port = 12345  # Choose an appropriate port number

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Send a UDP broadcast
message = "Hello, server!"
udp_socket.sendto(message.encode(), (broadcast_ip, broadcast_port))

print(f"Sent UDP broadcast to {broadcast_ip}:{broadcast_port}")

# Close the socket
udp_socket.close()

# Uncomment the following line to run the client
# send_udp_broadcast()