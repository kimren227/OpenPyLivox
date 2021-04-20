import socket
import sys
import time

ip = '127.0.0.1'
port = 6006

# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

# Let's send data through UDP protocol
b = bytearray("12358713258967123596781235678125678132", "utf8")
start_time = time.time()
for i in range(10):
    s.sendto(b, (ip, port))
print(time.time() - start_time)
# close the socket
s.close()