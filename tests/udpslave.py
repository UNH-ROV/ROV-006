# Listens for a udp packet and considers the IP address in that packet the master
# Assumes a singular interface on the slave device. Otherwise we are at the will
# of the kernel
import socket

PORT=30002
HOST="::"
INIT_RESPONSE=b"Hi"

def main():
    recvsock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # IPv4 UDP
    # I've found no need to join the ff02::1 multicase group
    recvsock.bind(('', PORT))

    sendsock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # IPv4 UDP

    # Wait for a master broadcast
    while True:
        data, addr = recvsock.recvfrom(512)
        if data == b'UNHROV':
            sendsock.sendto(INIT_RESPONSE, (addr[0], PORT))
            break

main()
