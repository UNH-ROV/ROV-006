"""
  NOTE: The firmware on the IMU sets gravity as 256.
  I don't really know what unit this is.
  From firmware docs:
      Axis definition (differs from definition printed on the board!):
      X axis pointing forward (towards the short edge with the connector holes)
      Y axis pointing to the right and Z axis pointing down.

      Positive yaw   : clockwise
      Positive roll  : right wing down
      Positive pitch : nose up

      Transformation order: first yaw then pitch then roll.

   Serial commands that the firmware understands:
   "#b" - Output sensors in BINARY format - acc, gyro (3 floats for each sensor so output frame is 24 bytes)
   "#t" - Output angles in TEXT format (Output frames have form like "#A142.28,-5.38,33.52#G-142.28,-5.38,33.52
   followed by carriage return and line feed [\r\n]).

   Byte order of binary output is little-endian: least significant byte comes first.
"""
import serial
import struct
import time

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
WRITE_WAIT = 0.01
MESSAGE_SIZE = 24

class IMU(serial.Serial):
    def __init__(self, dev, rate):
        serial.Serial.__init__(self, dev, rate)
        time.sleep(2) # This should be more than 1 second.

        self.flushInput() # Deprecated 
        #self.reset_input_buffers() New version

    def read_bin(self):
        self.write(b'#b')
        self.flush()
        time.sleep(WRITE_WAIT)

        line = self.read(24)
        unpacked = struct.unpack('<ffffff', line)

        return unpacked[0:3], unpacked[3:6]

    def read_text(self):
        """ Briefly enters text output and returns reply."""
        self.write(b'#t')
        self.flush()
        time.sleep(WRITE_WAIT)

        return self.readline()

if __name__ == '__main__':
    """ Poll the imu at random intervals and output the values.
        The internal poll rate of the firmware is 20ms(50Hz)
        so polling faster than that is pointless
    """
    import random
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    while True:
        accel, gyro = imu.read_bin()

        print("A: {}".format(accel))
        print("G: {}".format(gyro))
        #print(imu.read_text())

        time.sleep(random.random() * 0.1 + 0.1)
