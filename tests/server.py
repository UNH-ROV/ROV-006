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
TARGET_HOST="192.168.0.15"
UDP_RATE=50     # ms between each datagram. 50 = 20 packets/s

# This will be modified by the xbox button handlers
controller_info = {
    "lx" : 0.0,
    "ly" : 0.0,
    "rx" : 0.0,
    "ry" : 0.0,
    "lt" : 0.0,
    "rt" : 0.0,
    "a" : 0,
}

class TransportProtocol:
    """ Implement callbacks for asyncio transports
    """
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data = data.decode()
        print(data)

    def error_received(self, exc):
        print('error:', exc)

def stick_l(x, y):
    global controller_info
    controller_info["lx"] = round(x, 2)
    controller_info["ly"] = round(y, 2)

def stick_r(x, y):
    global controller_info
    controller_info["rx"] = round(x, 2)
    controller_info["ry"] = round(y, 2)

def trig_l(x):
    global controller_info
    controller_info["lt"] = round(x, 2)

def trig_r(x):
    global controller_info
    controller_info["rt"] = round(x, 2)

def button_a():
    global controller_info
    controller_info["a"] = 1

async def controller_output():
    """Read xbox controller information.
    """
    joy = await xbox_async.Joystick.create(normalize=True)
    joy.on_button(Button.LStick, stick_l)
    joy.on_button(Button.RStick, stick_r)
    joy.on_button(Button.LTrigger, trig_l)
    joy.on_button(Button.RTrigger, trig_r)
    joy.on_button(Button.A, button_a)

    while True:
        joy = await joy.read()

    joy.close()

async def send_data(transport, interval):
    """Send UDP packet through given transport of some global data every interval(ms)
    I am a bit cautious of packet sizes, but it likely won't matter.
    """
    global controller_info

    while True:
        await asyncio.sleep(interval / 1000.0)

        # Package all the global vars into JSON and send it.
        controller_info_json = json.dumps(controller_info)

        # The transport should already have destination specification stored in it.
        # Otherwise we can specify it.
        transport.sendto(controller_info_json.encode())


        # Send certain messages only one time
        if "a" in controller_info:
            del controller_info["a"]

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
        TransportProtocol,
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
