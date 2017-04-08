# NOTE: The firmware on the IMU sets gravity as 256.
# I don't really know what unit this is.
"""From firmware docs:
  Axis definition (differs from definition printed on the board!):
    X axis pointing forward (towards the short edge with the connector holes)
    Y axis pointing to the right
    and Z axis pointing down.

  Positive yaw   : clockwise
  Positive roll  : right wing down
  Positive pitch : nose up

  Transformation order: first yaw then pitch then roll.

  "#oscb" - Output CALIBRATED SENSOR data of all 9 axes in BINARY format.
  "#s<xy>" - Request synch token - useful to find out where the frame boundaries are in a continuous
         binary stream or to see if tracker is present and answering. The tracker will send
  "#SYNCH<xy>\r\n" in response (so it's possible to read using a readLine() function).
     x and y are two mandatory but arbitrary bytes that can be used to find out which request
     the answer belongs to.
"""
import serial
import struct
import time

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
WRITE_WAIT = 0.01
MESSAGE_SIZE = 36

class IMU(serial.Serial):
    def __init__(self, dev, rate):
        serial.Serial.__init__(self, dev, rate)
        time.sleep(3)

        #self.write(b'#o0#ob')
        self.write(b'#o0#oscb#sab')
        self.flush()
        time.sleep(WRITE_WAIT) # Wait for write

        # Read lines until the sync token is received
        while True:
            line = self.readline();
            if line.endswith("#SYNCHab\r\n"):
                break

    def get_sensors(self):
        """ Expects the IMU to be configured to output all sensor data. """
        self.write(b'#f')
        self.flush()
        time.sleep(WRITE_WAIT) # Wait for write

        line = self.read(MESSAGE_SIZE)
        unpacked = struct.unpack('fffffffff', line)

        # accel, mag, gyro
        return unpacked[0:3], unpacked[3:6], unpacked[6:9]

if __name__ == '__main__':
    """ Poll the imu at random intervals. Print the rolling accel average.
        The internal poll rate of the firmware is 20ms(50Hz)
        so polling faster than that is pointless
    """
    import random
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)
    avgX = 0
    avgY = 0
    avgZ = 0
    count = 0
    while True:
        accel, mag, gyro = imu.get_sensors()
        avgX = (avgX * count + accel[0]) / (count + 1)
        avgY = (avgY * count + accel[1]) / (count + 1)
        avgZ = (avgZ * count + accel[2]) / (count + 1)
        count += 1
        #print("ACC:", accel)
        #print("MAG:", mag)
        #print("GYRO:", gyro)
        print("Average accelerometer data: {}, {}, {}".format(avgX, avgY, avgZ))
        time.sleep(random.random() * 0.1 + 0.1)
