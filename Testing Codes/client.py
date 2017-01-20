#!/usr/bin/env python3
import socket
import json

import ThrusterControl.py

PORT=30002

def handle_data(data):
    print(data)
    if data["pos_x"]:
        print("pos_x: %d", data["pos_x"])
    if data["pos_y"]:
        print("pos_y: %d", data["pos_y"])

"""Implement callbacks for asyncio transports
"""
class clientprotocol:
    def __init__(self, loop):
        self.loop = loop
        self.transport = none

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data_json = data.decode()
        data = json.loads(data_json)
        handle_data(data)

    def error_received(self, exc):
        print('error:', exc)

# Control for the ROV.
if __name__ == "__main__":
    # Create event loop for both Windows/Unix. I'm not sure if the entire code base is cross-platform
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())

    # Init UDP transport channel
    connect = loop.create_datagram_endpoint(
        lambda: ClientProtocol(loop))
    loop.run_until_complete(connect)

    # Do stuff here.
    # loop.run_forever()

    transport.close()
    loop.close()
