#!/usr/bin/env python3
""" Logic for the ROV.
"""
import asyncio
import json
import signal
import socket
import sys
import Adafruit_PCA9685

from bar30 import Bar30
from thruster_manager import Thrusters

LOCAL_ADDR="192.168.0.15"
TARGET_ADDR="192.168.0.14"
PORT=30002
THRUSTER_RATE=100     # ms between each thruster signal. 50 = 20 signals/s
PWM_FREQ = 48
CONTROLLER_DEADZONE=0.2

# Updated by handle_data method
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

class TransportProtocol:
    """Implement callbacks for asyncio transports
    """
    def __init__(self, loop, pwm):
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
    #controller_info["a"] = data["a"]
    #controller_info["y"] = data["y"]

    print(data)
    # DEADZONE
    if data["lx"] < CONTROLLER_DEADZONE:
        data["lx"] = 0
    if data["ly"] < CONTROLLER_DEADZONE:
        data["ly"] = 0
    if data["rx"] < CONTROLLER_DEADZONE:
        data["rx"] = 0
    if data["ry"] < CONTROLLER_DEADZONE:
        data["ry"] = 0
    # Create tasks for command buttons
    #if data["a"] == 1:
        #asyncio.async(loop.create_task(get_temp(transport)), loop=loop)
    #if data["y"] == 1:
        #asyncio.async(loop.create_task(light_toggle(self.pwm)), loop=loop)

@asyncio.coroutine
def control_thruster(interval, pwm):
    """ Reads controller_info and sends the proper command to ThrusterControl library. """
    global controller_info
    thrusters = Thrusters(pwm)

    while True:
        yield from asyncio.sleep(interval / 1000.0)

        thrusters.move_horizontal(controller_info["lx"])
        thrusters.move_forward(controller_info["ly"])
        thrusters.move_vertical(controller_info["lt"] - controller_info["rt"])
        thrusters.move_yaw(-controller_info["rx"])
        thrusters.move_pitch(controller_info["ry"])

        thrusters.drive()

@asyncio.coroutine
def light_toggle(pwm):
    # If light hasn't been initialized, init it
    global light
    try:
        light
    except NameError:
        light = Light(pwm)

    light.toggle();

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

    (temp_c, pressure) = yield from temp_bar.read_bar()

    # TEMP HACK: Make a new socket and send
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(("T:%f,P:%f" % temp_c, pressure).encode(), (TARGET_ADDR, PORT))
    print("Temp: %f, Pressure = %f" % temp_c, pressure)

if __name__ == "__main__":
    # Create event loop for both Windows/Unix. I'm not sure if the entire code base is cross-platform
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    #loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())

    # Init pi hat
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo

    # Init two UDP transport channel
    # Listener
    connect = loop.create_datagram_endpoint(
        lambda: TransportProtocol(loop, pwm),
        local_addr = (LOCAL_ADDR, PORT))
    transport, protocol = loop.run_until_complete(connect)


    tasks = [
        #asyncio.ensure_future(control_thruster(THRUSTER_RATE, pwm))
        asyncio.async(control_thruster(THRUSTER_RATE, pwm))
    ]

    loop.run_until_complete(asyncio.gather(*tasks));
    #loop.run_until_complete(asyncio.gather(control_thruster(THRUSTER_RATE)))

    transport.close()
    loop.close()

