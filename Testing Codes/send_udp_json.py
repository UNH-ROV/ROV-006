import json
import socket

# HOST and INTERFACE will likely have to be hard coded for each master.
PORT=30002
HOST="192.168.1.166"
TARGET_HOST="192.168.1.166"

if __name__ == "__main__":
    recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
    recvsock.bind(('', PORT))

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

    data = {}
    data['pos_x'] = 1234
    data['pos_y'] = "43"

    data_json = json.dumps(data)
    sendsock.sendto(data_json.encode(), (TARGET_HOST, PORT))

    recvdata_json, addr = recvsock.recvfrom(512, socket.MSG_DONTWAIT)
    recvdata = json.loads(recvdata_json)
    print(recvdata_json)
    print("Hi")
    print(recvdata)
    print(recvdata['pos_x'])

