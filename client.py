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
from light import Light
from thruster_manager import Thrusters

LOCAL_ADDR="192.168.0.15"
TARGET_ADDR="192.168.0.14"
PORT=30002
THRUSTER_RATE=100     # ms between each thruster signal. 50 = 20 signals/s
PWM_FREQ = 48
CONTROLLER_DEADZONE=0.2

LIGHT_PIN = 11

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

class UDP:
    """Implement callbacks for asyncio transports
        Use to receive controller info
    """
    def __init__(self, loop, pwm):
        self.loop = loop
        self.pwm = pwm

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        data_json = data.decode()
        try:
            data = json.loads(data_json)
            handle_data(data, self.loop)
        except json.JSONDecodeError:
            print("Received invalid packet.")
            pass    # Ignore non JSON packets
        except e:
            print(e)

    def error_received(self, exc):
        print('UDP connection error:', exc)

def handle_data(data, loop):
    """Parses JSON from UDP packets.
    Adds data to global variable.
    """
    global controller_info
    controller_info = data

    # DEADZONE
    if controller_info["lx"] < CONTROLLER_DEADZONE:
        controller_info["lx"] = 0
    if controller_info["ly"] < CONTROLLER_DEADZONE:
        controller_info["ly"] = 0
    if controller_info["rx"] < CONTROLLER_DEADZONE:
        controller_info["rx"] = 0
    if controller_info["ry"] < CONTROLLER_DEADZONE:
        controller_info["ry"] = 0


    # Create tasks for command buttons
    if controller_info["a"] == 1:
        loop.create_task(get_temp())
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

    light.toggle()

@asyncio.coroutine
def get_temp():
    """ Gets temperature and prints it out.
    """
    global temp_bar, sock
    print("Trying to get thruster data.")
    # Check if things have been initialized
    try:
        temp_bar
    except NameError:
        temp_bar = Bar30()
    try:
        sock
    except NameError:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TARGET_ADDR, PORT))

    (temp_c, pressure) = yield from temp_bar.read_bar()

    sock.send(("T:%f,P:%f" % (temp_c, pressure)).encode())
    #print("Temp: %f, Pressure = %f" % (temp_c, pressure))

if __name__ == "__main__":
    # Create event loop for both Windows/Unix. I'm not sure if the entire code base is cross-platform
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    # Init pi hat
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo

    # Turn on light
    lights = Light(pwm, LIGHT_PIN)
    lights.set_on()

    # Init UDP Server
    recv = loop.create_datagram_endpoint(
        lambda: UDP(loop, pwm),
        local_addr = (LOCAL_ADDR, PORT))
    transport, protocol = loop.run_until_complete(recv)

    tasks = [
        #asyncio.ensure_future(control_thruster(THRUSTER_RATE, pwm)) Python 3.5
        asyncio.async(control_thruster(THRUSTER_RATE, pwm))
    ]

    # Exit handler
    loop.add_signal_handler(signal.SIGINT, lambda: (transport.close(), loop.stop()))

    loop.run_until_complete(asyncio.gather(*tasks));

    transport.close()
    loop.close()

