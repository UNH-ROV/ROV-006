"""
Output the average of data points
"""
import time
import random
from devices.imu import IMU

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600

if __name__ == '__main__':
    """ Poll the imu at random intervals and output the average
    """
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    avg_accel = [0.0, 0.0, 0.0]
    avg_gyro = [0.0, 0.0, 0.0]
    count = 0
    while True:
        accel, gyro = imu.read_bin()

        avg_accel = [ (avg * count + new) / (count + 1) for avg, new in zip(avg_accel, accel)]
        avg_gyro = [ (avg * count + new) / (count + 1) for avg, new in zip(avg_gyro, gyro)]
        count += 1

        print("A: {}-----G: {}".format(avg_accel, avg_gyro))

        # Sleeps from 100-200ms
        time.sleep(random.random() * 0.1 + 0.1)
