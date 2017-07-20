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
from HLController import HLController

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
LOCAL_ADDR="192.168.0.15"
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
}
autonomy = False

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
            handle_udpdata(data, self.loop, self.pwm)
        except json.JSONDecodeError:
            print("Received invalid packet.")
            pass    # Ignore non JSON packets
        except e:
            print(e)

    def error_received(self, exc):
        print('UDP connection error:', exc)

def handle_udpdata(data, loop, pwm):
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

class TCP(asyncio.Protocol):
    """ Implement callbacks for asyncio transports.
        This will be used to send receive info from the ROV, i.e. temperature data
    """
    def __init__(self, pwm):
        self.pwm = pwm

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        if data == 'temp':
            pressure, temp = get_temp()
            self.transport.write("T: {}mbar, P: {}C".format(temp, pressure).encode())
        elif data == 'light':
            light_toggle(self.pwm)
        elif data == 'auto':
            autonomy = not autonomy
        elif data.startswith('pid'):
            pass
        elif data.startswith('lqr'):
            pass

    def error_received(self, exc):
        print('TCP connection error:', exc)

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
        print("Initializing temperature bar.")
        get_temp.temp_bar = ms5837.MS5837()
        if not get_temp.temp_bar.init():
            print("Sensor failed to initialize")

    bar.read()

    pressure = bar.pressure(ms5837.UNITS_mbar)
    temp = bar.temperature(ms5837.UNITS_Centigrade)

    return pressure, temp

def light_toggle(pwm):
    try:
        light_toggle.toggle()
    except AttributeError:
        light = Light(pwm, LIGHT_PIN)
        light.set_on()
        light.toggle()

@asyncio.coroutine
def manual_loop(interval, thrusters):
    """ Reads controller_info and sends the proper command to ThrusterControl library. """
    global controller_info, autonomy

    while True:
        yield from asyncio.sleep(interval / 1000.0)
        if not autonomy:
            thrusters.move_horizontal(controller_info["lx"])
            thrusters.move_forward(controller_info["ly"])
            thrusters.move_vertical(controller_info["lt"] - controller_info["rt"])
            thrusters.move_yaw(-controller_info["rx"]) # Flipped to map xbox state to ROV coordinate
            thrusters.move_pitch(controller_info["ry"])

            thrusters.drive()

@asyncio.coroutine
def auto_loop(interval, thrusters):
    """ Constantly updates controller with IMU data.
    """
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)
    controller = HLController()

    while True:
        yield from asyncio.sleep(interval / 1000.0)

        accel, mag, gyro = imu.get_sensors()
        weights = controller.update(accel, gyro)

        if autonomy:
            thrusters.move_horizontal(weights[0])
            #thrusters.move_forward(weights[1])
            #thrusters.move_vertical(weights[2])
            #thrusters.move_yaw(-weights[3])
            #thrusters.move_pitch(weights[4])
            #thrusters.move_pitch(weights[5])

        thrusters.drive()


        print("From accel:{} and gyro:{} || Pos:{}, Rot:{}, Vel{}".format(accel, gyro, controller.position, controller.rotation, controller.velocity))

if __name__ == "__main__":
    # asyncio loop
    loop = asyncio.get_event_loop()

    # Init pi hat
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo

    # Init lights and thrusters
    Light(pwm, LIGHT_PIN).set_on() # We drop the class
    thrusters = Thrusters(pwm)

    # Init UDP Server
    udp_serv = loop.create_datagram_endpoint(
        lambda: UDP(loop, pwm),
        local_addr = (LOCAL_ADDR, PORT))
    transport, protocol = loop.run_until_complete(udp_serv)

    # Init TCP Server
    tcp_serv = loop.create_server(TCP, LOCAL_ADDR, PORT)
    server = loop.run_until_complete(tcp_serv)

    # define tasks
    tasks = [
        #Python3.5 asyncio.ensure_future(manual_loop(THRUSTER_RATE, pwm))
        asyncio.async(manual_loop(THRUSTER_RATE, thrusters)),
        asyncio.async(auto_loop(THRUSTER_RATE, thrusters)),
    ]

    loop.add_signal_handler(signal.SIGINT, lambda: (transport.close(), loop.stop(), server.close()))
    loop.run_until_complete(asyncio.gather(*tasks));
