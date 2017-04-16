#!/usr/bin/env python3
""" Logic for the ROV.
"""
import asyncio
import json
import signal
import sys

import bar30
from thruster_manager import Thrusters

LOCAL_ADDR="192.168.0.15"
PORT=30002
THRUSTER_RATE=100     # ms between each thruster signal. 50 = 20 signals/s

# Updated by handle_data method
controller_info = {}

class TransportProtocol:
    """Implement callbacks for asyncio transports
    """
    def __init__(self, loop):
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data_json = data.decode()
        try:
            data = json.loads(data_json)
            handle_data(data, self.transport, self.loop)
        except json.JSONDecodeError:
            print("Received invalid packet.")
            pass    # Ignore non JSON packets

    def error_received(self, exc):
        print('error:', exc)

def handle_data(data, transport, loop):
    """Parses JSON from UDP packets.
    Adds data to global variable.
    """
    global controller_info

    # Update global structure.
    controller_info["lx"] = data["lx"]
    controller_info["ly"] = data["ly"]
    controller_info["rx"] = data["rx"]
    controller_info["ry"] = data["ry"]
    controller_info["lt"] = data["lt"]
    controller_info["rt"] = data["rt"]
    controller_info["a"] = data["a"]

    # Create tasks for command buttons
    if data["a"] == 1:
        loop.create_task(get_temp(transport))

@asyncio.coroutine
def control_thruster(interval):
    """ Reads controller_info and sends the proper command to ThrusterControl library. """
    global controller_info
    thrusters = Thrusters()

    while True:
        yield from asyncio.sleep(interval / 1000.0)

        thrusters.move_horizontal(controller_info["lx"])
        thrusters.move_forward(controller_info["ly"])
        thrusters.move_vertical(controller_info["lt"] - controller_info["rt"])
        thrusters.move_yaw(controller_info["rx"])
        thrusters.move_pitch(controller_info["ry"])

        thrusters.drive()

@asyncio.coroutine
def get_temp(transport):
    """ Gets temperature and prints it out.
    """
    global temp_bar

    # If temp_bar hasn't been initialized, init it
    try:
        temp_bar
    except NameError:
        temp_bar = Bar30()

    (temp_c, pressure) = yield temp_bar.read_bar()

    # TODO: Send a UDP packet
    # transport.sendto(("T:%f,P:%f" % temp_c, pressure).encode())
    print("Temp: %f, Pressure = %f" % temp_c, pressure)

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
        lambda: TransportProtocol(loop),
        local_addr = (LOCAL_ADDR, PORT))
    transport, protocol = loop.run_until_complete(connect)


    tasks = [
        asyncio.ensure_future(control_thruster(THRUSTER_RATE))
    ]

    loop.run_until_complete(asyncio.gather(*tasks));
    #loop.run_until_complete(asyncio.gather(control_thruster(THRUSTER_RATE)))

    transport.close()
    loop.close()

