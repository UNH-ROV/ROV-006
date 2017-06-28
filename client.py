#!/usr/bin/env python3
""" Logic for the ROV.
"""
import asyncio
import json
import serial
import signal
import socket
import sys
import time
import Adafruit_PCA9685

import devices.ms5837 as ms5837 # Temp & Pressure sensor
from devices.imu import IMU
from devices.light import Light
from devices.t100 import Thrusters

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
LOCAL_ADDR="192.168.0.15"
TARGET_ADDR="192.168.0.14"
PORT=30002
THRUSTER_RATE=100     # ms between each thruster signal. 50 = 20 signals/s
PWM_FREQ = 48
CONTROLLER_DEADZONE=0.2
LIGHT_PIN = 15
# Pins for thrusters are defined in the thruster module; Sorry! it's 8 pins!

COMMAND_LIMIT = 1 # seconds between each command. i.e. temp sensor

# Updated by handle_data method
controller_info = {
    "lx" : 0.0,
    "ly" : 0.0,
    "rx" : 0.0,
    "ry" : 0.0,
    "lt" : 0.0,
    "rt" : 0.0,
    "a" : 0,
    "y" : 0,
    "g" : 0,
}
temp_time = 0  # Previous time temp was retrieved.
light_time = 0 # Previous time light was toggled.

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
            handle_data(data, self.loop, self.pwm)
        except json.JSONDecodeError:
            print("Received invalid packet.")
            pass    # Ignore non JSON packets
        except e:
            print(e)

    def error_received(self, exc):
        print('UDP connection error:', exc)

def handle_data(data, loop, pwm):
    """Parses JSON from UDP packets.
    Adds data to global variable.
    """
    global controller_info, temp_time, light_time
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
    # The nature of the station may send a lot of these command signals, rate limit these tasks.
    if controller_info["a"] or controller_info["y"]:
        curr_time = time.time()
        if controller_info["a"] and curr_time - temp_time > COMMAND_LIMIT:
            loop.create_task(get_temp())
            temp_time = curr_time
        if controller_info["y"] and curr_time - light_time > COMMAND_LIMIT:
            loop.create_task(light_toggle(pwm))
            light_time = curr_time

@asyncio.coroutine
def core_loop(interval, pwm):
    """ Reads controller_info and sends the proper command to ThrusterControl library. """
    global controller_info
    thrusters = Thrusters(pwm)
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

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
    try:
        light_toggle.toggle()
    except AttributeError:
        light = Light(pwm, LIGHT_PIN)
        light.set_on()
        light.toggle()

@asyncio.coroutine
def get_temp():
    """ Gets temperature and sends the information into the socket.
        temp_bar and sock are static variables.
    """
    try:
        bar = get_temp.temp_bar
        sock = get_temp.sock
    except AttributeError:
        # This was the first time this function was run.
        # Initialize all static vars.
        get_temp.temp_bar = ms5837.MS5837()
        if not get_temp.temp_bar.init():
            print("Sensor failed to initialize")

        get_temp.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        get_temp.sock.connect((TARGET_ADDR, PORT))

    bar.read()

    pressure = bar.pressure(ms5837.UNITS_mbar)
    temp = bar.temperature(ms5837.UNITS_Centigrade)

    # TODO: sock send asyncio
    sock.send(("T:%f,P:%f" % (temp, pressure)).encode())
    #print("Temp: %f, Pressure = %f" % (temp_c, pressure))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Exit handler
    loop.add_signal_handler(signal.SIGINT, lambda: (transport.close(), loop.stop()))

    # Init pi hat
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo

    # Turn on light
    Light(pwm, LIGHT_PIN).set_on()

    # Init UDP Server
    recv = loop.create_datagram_endpoint(
        lambda: UDP(loop, pwm),
        local_addr = (LOCAL_ADDR, PORT))
    transport, protocol = loop.run_until_complete(recv)

    tasks = [
        #Python3.5 asyncio.ensure_future(core_loop(THRUSTER_RATE, pwm))
        asyncio.async(core_loop(THRUSTER_RATE, pwm)),
    ]

    loop.run_until_complete(asyncio.gather(*tasks));

    transport.close()
    loop.close()
