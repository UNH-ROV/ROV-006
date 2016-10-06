# Sends a broadcast udp packet, all slaves should respond.
import socket
import time
import struct

# HOST and INTERFACE will likely have to be hard coded for each master.
PORT=30002
HOST="fe80::82ee:73ff:feab:38c1"
INTERFACE="eth0"
SLAVE_WAIT_TIME=5 # seconds to wait for slaves to respond to broadcast
INIT_MESSAGE=b"UNHROV"

def create_socket(ifn=""):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # IPv6, UDP
    # Allows multiple programs to bind to this addr
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Some default IPv6 setup
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 5) # Might want to raise this

    ifn = socket.if_nametoindex(ifn)
    ifn = struct.pack("I", ifn)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, ifn)

    return sock, ifn


# Broadcast a packet with our init string.
# Slaves will communicate back with their IPs
def get_slaves():
    # Setup a temporary UDP listener on the same port we are broadcasting to
    recvsock, recvif = create_socket(INTERFACE)
    recvsock.bind(('', PORT))
    # TODO: Properly bind to the correct interface. This binds to default network interface,
    # even if you define a flow and scope id.

    sendsock, sendif = create_socket(INTERFACE)

    slaves = []
    for _ in range(SLAVE_WAIT_TIME):
        sendsock.sendto(INIT_MESSAGE, ("ff02::1", PORT))
        try:
            while True:
                data, addr = recvsock.recvfrom(512, socket.MSG_NOWAIT)
                print("Hot one!")
                slaves.append(addr)
        except:
            pass
        time.sleep(1)

    return set(slaves)

def main():
    if not socket.has_ipv6:
        print("We don't support IPv6, abandon ship!!!!!")
        quit()

    slaves = get_slaves();
    print(slaves)

main()
