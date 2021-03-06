""" MS5837-30BA Pressure/Temperature sensor code.
See MS5837-30BA data spec for why these calculations take place.

Sensor: MS5837_30BA Bar30 Pressure/Temperature Sensor (BlueRobotics)
Original code: https://github.com/ControlEverythingCommunity/MS5836-30BA01
Modified by: Sital Khatiwada, Christopher Chin

Before you run this code, ensure that:
1. I2C pins are enabled on the Raspberry Pi
2. Install i2c-tools on the Raspberry Pi
3. Install python-smbus on the Raspberry Pi
"""

import smbus
import time
import asyncio

SLEEP_TIME=500 # ms

class Bar30:
    def __init__(self):
        # Get I2C bus
        self.bus = smbus.SMBus(1)

        # MS5837_30BA01 address, 0x76(118)
        #		0x1E(30)	Reset command
        self.bus.write_byte(0x76, 0x1E)

        time.sleep(0.5)
        self.calibrate()

    """ Read calibration data and store them, from what I can
    gather from the spec sheet, this needs to only be done once
    """
    def calibrate(self):
        # Read 12 bytes of calibration data
        # Read pressure sensitivity
        data = self.bus.read_i2c_block_data(0x76, 0xA2, 2)
        self.C1 = data[0] * 256 + data[1]

        # Read pressure offset
        data = self.bus.read_i2c_block_data(0x76, 0xA4, 2)
        self.C2 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure sensitivity
        data = self.bus.read_i2c_block_data(0x76, 0xA6, 2)
        self.C3 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure offset
        data = self.bus.read_i2c_block_data(0x76, 0xA8, 2)
        self.C4 = data[0] * 256 + data[1]

        # Read reference temperature
        data = self.bus.read_i2c_block_data(0x76, 0xAA, 2)
        self.C5 = data[0] * 256 + data[1]

        # Read temperature coefficient of the temperature
        data = self.bus.read_i2c_block_data(0x76, 0xAC, 2)
        self.C6 = data[0] * 256 + data[1]

    @asyncio.coroutine
    def read_bar(self):
        """ Returns (temperature, pressure). Temp is in Celsius.
        The two can't really by seperated because they are dependant on each other!
        Chains into a lengthy sleep. So likely dump this in its own task.
        """
        # MS5837_30BA01 address, 0x76(118)
        #		0x40(64)	Pressure conversion(OSR = 256) command
        self.bus.write_byte(0x76, 0x40)

        yield from asyncio.sleep(SLEEP_TIME / 1000.0)

        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.bus.read_i2c_block_data(0x76, 0x00, 3)
        D1 = value[0] * 65536 + value[1] * 256 + value[2]

        # MS5837_30BA01 address, 0x76(118)
        #		0x50(64)	Temperature conversion(OSR = 256) command
        self.bus.write_byte(0x76, 0x50)

        yield from asyncio.sleep(SLEEP_TIME / 1000.0)

        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = self.bus.read_i2c_block_data(0x76, 0x00, 3)
        D2 = value[0] * 65536 + value[1] * 256 + value[2]

        dT = D2 - self.C5 * 256
        TEMP = 2000 + dT * self.C6 / 8388608
        OFF = self.C2 * 65536 + (self.C4 * dT) / 128
        SENS = self.C1 * 32768 + (self.C3 * dT ) / 256
        T2 = 0
        OFF2 = 0
        SENS2 = 0

        if TEMP >= 2000:
            T2 = 2 * (dT * dT) / 137438953472
            OFF2 = ((TEMP - 2000) * (TEMP - 2000)) / 16
            SENS2 = 0
        else:
            T2 = 3 * (dT * dT) / 8589934592
            OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 2
            SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 8
            if TEMP < -1500:
                OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 4 * ((TEMP + 1500) * (TEMP + 1500))

        TEMP = TEMP - T2
        OFF2 = OFF - OFF2
        SENS2 = SENS - SENS2

        pressure = ((((D1 * SENS2) / 2097152) - OFF2) / 8192) / 10.0
        temp_c = TEMP / 100.0
        #tempF = temp_c * 1.8 + 32

        return (temp_c, pressure)
