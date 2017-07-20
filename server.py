#!/usr/bin/env python3
""" Logic for the master device controlling the ROV.
Current setup:
    Send a UDP message with controller_info to the
    TARGET_HOST on PORT every UDP_RATE ms.
    Send a TCP message with single time events
"""
import devices.xbox_async
from devices.xbox_async import Button, Joystick
import asyncio
import sys
import signal
import time
import socket
import json
#import gbulb

#gbulb.install()

PORT=30002
LOCAL_ADDR="192.168.0.14"
TARGET_ADDR="192.168.0.15"
UDP_RATE=50     # ms between each datagram. 50 = 20 packets/s
COMMAND_LIMIT = 1 # seconds between each command. i.e. temp sensor

# This will be modified by the xbox button handlers
controller_info = {
    "lx" : 0.0,
    "ly" : 0.0,
    "rx" : 0.0,
    "ry" : 0.0,
    "lt" : 0.0,
    "rt" : 0.0,
}

class UDP:
    """ Implement callbacks for asyncio transports.
        Our implementation has one-way communication for controller states.
    """
    def connection_made(self, transport):
        self.transport = transport

    def error_received(self, exc):
        print('UDP connection error:', exc)

class TCP(asyncio.Protocol):
    """ Implement callbacks for asyncio transports.
        Our implementation has one-way communication for controller states.
    """
    def connection_made(self, transport):
        print("TCP connection established")
        self.transport = transport

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

def req_temp():
    global rov_tcp_sock
    try: req_temp.time
    except AttributeError: req_temp.time = 0

    curr_time = time.time()
    if curr_time - req_temp.time > COMMAND_LIMIT:
        rov_tcp_sock.write("temp".encode())
    req_temp.time = curr_time

def req_light():
    global rov_tcp_sock
    try: req_light.time
    except AttributeError: req_light.time = 0

    curr_time = time.time()
    if curr_time - req_light.time > COMMAND_LIMIT:
        rov_tcp_sock.write("light".encode())
    req_light.time = curr_time

def req_auto():
    global rov_tcp_sock
    try: req_auto.time
    except AttributeError: req_auto.time = 0

    curr_time = time.time()
    if curr_time - req_auto.time > COMMAND_LIMIT:
        rov_tcp_sock.write("auto".encode())
    req_auto.time = curr_time


async def controller_poll():
    """Read xbox controller information.
    """
    joy = await Joystick.create(normalize=True)
    joy.on_button(Button.LStick, stick_l)
    joy.on_button(Button.RStick, stick_r)
    joy.on_button(Button.LTrigger, trig_l)
    joy.on_button(Button.RTrigger, trig_r)
    joy.on_button(Button.A, req_temp)
    joy.on_button(Button.B, req_light)
    joy.on_button(Button.X, req_auto)

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

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())

    # Init UDP client
    udp = loop.create_datagram_endpoint(
        lambda: UDP(), remote_addr=(TARGET_ADDR, PORT))
    transport, protocol = loop.run_until_complete(udp)

    # Init TCP client
    tcp = loop.create_connection(
        lambda: TCP(), TARGET_ADDR, PORT)

    tasks = [
        asyncio.ensure_future(tcp),
        asyncio.ensure_future(controller_poll()),
        asyncio.ensure_future(controller_output(transport, UDP_RATE))
    ]

    rov_tcp_sock, protocol = loop.run_until_complete(asyncio.gather(*tasks))

    transport.close()
    loop.close()
