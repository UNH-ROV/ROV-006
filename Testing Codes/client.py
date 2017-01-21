#!/usr/bin/env python3
""" Logic for the ROV.
"""
import asyncio
import json
import signal
import sys

#import bar30
#import ThrusterControl

PORT=30002

def handle_data(data):
    print(data)
    if "pos_x" in data:
        print("pos_x: %d" % data["pos_x"])
    if "pos_y" in data:
        print("pos_y: %d" % data["pos_y"])
    if "get_temp" in data:
        print("GET TEMPERATURE!!!!")

"""Implement callbacks for asyncio transports
"""
class ClientProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data_json = data.decode()
        data = json.loads(data_json)
        handle_data(data)

    def error_received(self, exc):
        print('error:', exc)

if __name__ == "__main__":
    # Create event loop for both Windows/Unix. I'm not sure if the entire code base is cross-platform
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    # Init UDP transport channel
    connect = loop.create_datagram_endpoint(
        ClientProtocol,
        local_addr = ('127.0.0.1', PORT))
    transport, protocol = loop.run_until_complete(connect)

    # Init bar30
    #temp_bar = Bar30()

    loop.run_forever()

    transport.close()
    loop.close()
