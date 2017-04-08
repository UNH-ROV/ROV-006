#!/usr/bin/env python3
""" Logic for the master device controlling the ROV.
Current setup:
    Send a UDP message to the TARGET_HOST on PORT every UDP_RATE ms.
    The packet will hold the controller state.
    Maintain a TCP connection for more explicit packets like sensor requests and responses.
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
LOCAL_ADDR="192.168.0.14"
TARGET_ADDR="192.168.0.15"
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
    "b" : 0,
    "x" : 0,
    "y" : 0,
}

class UDP:
    """ Implement callbacks for asyncio transports.
        Our implementation has one-way communication for controller states.
    """
    def connection_made(self, transport):
        self.transport = transport

    def error_received(self, exc):
        print('UDP connection error:', exc)

class TCPEchoServer(asyncio.Protocol):
    """ Implement callbacks for asyncio transports.
        This will be used to send receive info from the ROV, i.e. temperature data
    """
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print(data.decode())

    def error_received(self, exc):
        print('TCP connection error:', exc)

def stick_l(x, y):
    global controller_info
    controller_info["lx"] = x
    controller_info["ly"] = y

def stick_r(x, y):
    global controller_info
    controller_info["rx"] = x
    controller_info["ry"] = y

def trig_l(x):
    global controller_info
    controller_info["lt"] = x

def trig_r(x):
    global controller_info
    controller_info["rt"] = x

def button_a():
    global controller_info
    controller_info["a"] = 1

def button_x():
    global controller_info
    controller_info["x"] = 1

async def controller_poll():
    """Read xbox controller information.
    """
    joy = await xbox_async.Joystick.create(normalize=True)
    joy.on_button(Button.LStick, stick_l)
    joy.on_button(Button.RStick, stick_r)
    joy.on_button(Button.LTrigger, trig_l)
    joy.on_button(Button.RTrigger, trig_r)
    joy.on_button(Button.A, button_a)
    joy.on_button(Button.X, button_x)

    while True:
        joy = await joy.read()

    joy.close()

async def controller_output(transport, interval):
    """Send controller message through given transport every interval(ms)
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
            controller_info["a"] = 0
        if "x" in controller_info:
            controller_info["x"] = 0

if __name__ == "__main__":
    # Create event loop for both Windows/Unix. I'm not sure if the entire code base is cross-platform though
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())

    # Init UDP client
    send = loop.create_datagram_endpoint(
        lambda: UDP(),
        remote_addr=(TARGET_ADDR, PORT))
    transport, protocol = loop.run_until_complete(send)

    # Init TCP server
    coro = loop.create_server(TCPEchoServer, LOCAL_ADDR, PORT)
    recv = loop.run_until_complete(coro)

    tasks = [
        # Even though there is no UDP listener task, received packets will be handled
        asyncio.ensure_future(controller_poll()),
        asyncio.ensure_future(controller_output(transport, UDP_RATE))
    ]

    loop.run_until_complete(asyncio.gather(*tasks))

    transport.close()
    loop.close()
