#!/usr/bin/env python3
import xbox_async
from xbox_async import Button
import asyncio
import sys
import signal
import time
import socket
import json

PORT=30002
TARGET_HOST="192.168.1.166"
UDP_RATE=20     # 20 ms between each data packet

# This will be modified by the xbox button handlers
controller_info = {}

def positionStickHandle(x, y):
    global controller_info

    controller_info["pos_x"] = x
    controller_info["pos_y"] = y

def rotationStickHandle(x, y):
    global controller_info

    controller_info["rot_x"] = x
    controller_info["rot_y"] = y

"""Read xbox controller information.
"""
async def controllerOutput():
    joy = await xbox_async.Joystick.create()
    joy.onButton(Button.LStick, positionStickHandle)
    joy.onButton(Button.RStick, rotationStickHandle)

    while True:
        # TODO: See if joy.read() blocks
        joy = await joy.read()
        print("Hi")

    joy.close()

"""Send UDP packet through given transport of some global data every interval(ms)
"""
async def sendData(transport, interval):
    global controller_info
    while True:
        await asyncio.sleep(interval / 1000.0)
        # Package all the global vars into JSON and send it.
        controller_info_json = json.dumps(controller_info)

        # The transport should already have destination specification stored in it.
        # Otherwise we can specify it.
        transport.sendto(controller_info_json.encode())

"""Implement callbacks for asyncio transports
"""
class clientprotocol:
    def __init__(self, loop):
        self.loop = loop
        self.transport = none

    def connection_made(self, transport):
        self.transport = transport

    def error_received(self, exc):
        print('error:', exc)

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
        lambda: ClientProtocol(loop),
        remote_addr=(TARGET_HOST, PORT))
    loop.run_until_complete(connect)

    tasks = [
        asyncio.ensure_future(controllerOutput()),
        asyncio.ensure_future(sendData(transport, UDP_RATE))
    ]

    loop.run_until_complete(asyncio.gather(*tasks))

    transport.close()
    loop.close()
