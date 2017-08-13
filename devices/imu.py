"""
  NOTE: The firmware on the IMU sets gravity as 256.
  I don't really know what unit this is.

  See razor.ino for documentation.
  Binary output is little-endian.
"""
import serial
import struct
import time

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600

class IMU(serial.Serial):
    def __init__(self, dev, rate):
        serial.Serial.__init__(self, dev, rate)
        self.mode_bin()

        time.sleep(2) # This should be more than 1 second.

        self.flushInput() # Deprecated 
        #self.reset_input_buffers() New version

    def mode_bin(self):
        self.bin = True

        self.write(b'#b')
        self.flush()

    def mode_text(self):
        self.bin = False

        self.write(b'#t')
        self.flush()

    def get_sensors(self):
        self.write(b'#s')
        self.flush()

        if self.bin:
            line = self.read(24)
            unpacked = struct.unpack('<ffffff', line)

            return unpacked[0:3], unpacked[3:6]
        else:
            return self.readline()

    def get_angle(self):
        self.write(b'#a')
        self.flush()

        if self.bin:
            line = self.read(12)
            unpacked = struct.unpack('<fff', line)

            return unpacked
        else:
            return self.readline()

if __name__ == '__main__':
    """ Poll the imu at random intervals and output the values.
        The internal poll rate of the firmware is 20ms(50Hz)
        so polling faster than that is pointless
    """
    import random
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    while True:
        imu.mode_bin()
        accel, gyro = imu.get_sensors()

        print("A: {}".format(accel))
        print("G: {}".format(gyro))

        imu.mode_text()
        print(imu.get_sensors())

        print(imu.get_angle())

        time.sleep(random.random() * 0.1 + 0.1)
