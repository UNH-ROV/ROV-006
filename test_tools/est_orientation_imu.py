"""
Attempt to deduce position and orientation from IMU data

Gyros give angular velocity, so we can integrate it to find angle
Accelerometers
"""
import time
import random
from devices.imu import IMU

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600

position = [0, 0, 0]
orientation = [0, 0, 0]
velocity = [0, 0, 0]

if __name__ == '__main__':
    """ Poll the imu at random intervals and output the average
    """
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    prev_time = time.time();
    while True:
        #dt = 0.021
        dt = time.time() - prev_time
        print("dt {}".format(dt))

        accel, gyro = imu.read_bin()

        position = [x * dt for x in velocity]
        velocity = [x * dt for x in accel]
        orientation = [x * dt for x in gyro]

        # Sleeps for 21ms, approximately 50Hz 
        time.sleep(0.021)
