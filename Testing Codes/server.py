#!/usr/bin/env python3
""" Logic for the master device controlling the ROV.
Current setup:
    Send a UDP message to the TARGET_HOST on PORT every UDP_RATE ms. The packet
    will hold the controller state.
"""
import xbox_async
from xbox_async import Button
import asyncio
import sys
import signal
import time
import socket
import json

PORT=30002
TARGET_HOST="127.0.0.1"
UDP_RATE=50     # ms between each datagram. 50 = 20 packets/s

# This will be modified by the xbox button handlers
controller_info = {}

def stick_l(x, y):
    global controller_info
    controller_info["pos_x"] = x
    controller_info["pos_y"] = y

def stick_r(x, y):
    global controller_info
    controller_info["rot_x"] = x
    controller_info["rot_y"] = y

def read_temp():
    global controller_info
    controller_info["get_temp"] = 1

"""Read xbox controller information.
"""
async def controller_output():
    joy = await xbox_async.Joystick.create()
    joy.on_button(Button.LStick, stick_l)
    joy.on_button(Button.RStick, stick_r)
    joy.on_button(Button.A, read_temp)

    while True:
        joy = await joy.read()

    joy.close()

"""Send UDP packet through given transport of some global data every interval(ms)
"""
async def send_data(transport, interval):
    global controller_info
    while True:
        await asyncio.sleep(interval / 1000.0)
        # Package all the global vars into JSON and send it.
        controller_info_json = json.dumps(controller_info)

        # The transport should already have destination specification stored in it.
        # Otherwise we can specify it.
        transport.sendto(controller_info_json.encode())

        if "get_temp" in controller_info:
            del controller_info["get_temp"]

"""Implement callbacks for asyncio transports
"""
class ClientProtocol:
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
        ClientProtocol,
        remote_addr=(TARGET_HOST, PORT))
    transport, protocol = loop.run_until_complete(connect)

    tasks = [
        # Even though there is no UDP listener task, received packets will be handled
        asyncio.ensure_future(controller_output()),
        asyncio.ensure_future(send_data(transport, UDP_RATE))
    ]

    loop.run_until_complete(asyncio.gather(*tasks))

    transport.close()
    loop.close()
