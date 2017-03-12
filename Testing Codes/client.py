#!/usr/bin/env python3
""" Logic for the ROV.
Current status:
    Parses JSON on receiving UDP
TODO:
    Remove checks for "joy_x", etc. Use a try block and just fail to control.
"""
import asyncio
import json
import signal
import sys

import Bar30
import Thrusters

ADDR="10.21.121.213"
PORT=30002
THRUSTER_RATE=50     # ms between each thruster signal. 50 = 20 signals/s

controller_info = {}

class ClientProtocol:
    """Implement callbacks for asyncio transports
    """
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data_json = data.decode()
        try:
            data = json.loads(data_json)
            handle_data(data)
        except:
            pass    # Ignore non JSON packets

    def error_received(self, exc):
        print('error:', exc)

def handle_data(data, loop):
    """Parses JSON from UDP packets.
    Adds data to global variable.
    """
    global controller_info

    if "joy_x" in data:
        controller_info["joy_x"] = data["joy_x"];
    if "joy_y" in data:
        controller_info["joy_y"] = data["joy_y"];
    if "rot_y" in data:
        controller_info["rot_y"] = data["rot_y"];
    if "rot_y" in data:
        controller_info["rot_y"] = data["rot_y"];
    if "get_temp" in data:
        loop.create_task(get_temp())

async def control_thruster(interval):
    """ Reads controller_info and sends the proper command to ThrusterControl library. """
    thrusters = Thrusters()

    while True:
        await asyncio.sleep(interval / 1000.0)
        if "joy_x" in data:
            thrusters.move_forward(controller_info["joy_x"])
        if "joy_y" in data:
            thrusters.move_horizontal(controller_info["joy_y"])
        if "rot_x" in data:
            thrusters.move_yaw(controller_info["rot_x"])
        if "rot_y" in data:
            thrusters.move_pitch(controller_info["rot_y"])

        thrusters.driver()

async def get_temp():
    """ Gets temperature and prints it out.
    """
    global temp_bar

    # If temp_bar hasn't been initialized, init it
    try:
        temp_bar
    except NameError:
        temp_bar = Bar30()

    (temp_c, pressure) = await temp_bar.read_bar()
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
        ClientProtocol,
        local_addr = (ADDR, PORT))
    transport, protocol = loop.run_until_complete(connect)


    tasks = [
        asyncio.ensure_future(control_thruster(THRUSTER_RATE))
    ]

    loop.run_until_complete(asyncio.gather(*tasks));

    transport.close()
    loop.close()
