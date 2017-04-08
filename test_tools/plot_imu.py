""" Plots a certain value from the IMU."""
import random
import numpy as np
import matplotlib.pyplot as plt
from devices.imu import IMU

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
DATA_POINTS = 500

if __name__ == '__main__':
    """ Poll the imu at random intervals and plot stuff.
        The internal poll rate of the firmware is 20ms(50Hz)
        so polling faster than that is pointless
    """
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    accel_data = [[], [], []]
    time_data = []

    start_time = time.time()
    for _ in range(0, DATA_POINTS):
        accel, gyro = imu.read_bin()

        accel_data[0].append(accel[0])
        accel_data[1].append(accel[1])
        accel_data[2].append(accel[2])

        time_data.append(time.time() - start_time)
        time.sleep(random.random() * 0.1 + 0.1)

    xfig = plt.figure(figsize=(10, 7))
    plt.plot(time_data, accel_data[0], label='X')
    plt.xlabel('time(s)')
    plt.ylabel('X')
    plt.yticks(np.arange(min(accel_data[0]), max(accel_data[0])+1, 0.25))

    yfig = plt.figure(figsize=(10, 7))
    plt.plot(time_data, accel_data[1], label='Y')
    plt.xlabel('time(s)')
    plt.ylabel('Y')
    plt.yticks(np.arange(min(accel_data[1]), max(accel_data[1])+1, 0.25))

    zfig = plt.figure(figsize=(10, 7))
    plt.plot(time_data, accel_data[2], label='Z')
    plt.xlabel('time(s)')
    plt.ylabel('Z')
    plt.yticks(np.arange(min(accel_data[2]), max(accel_data[2])+1, 0.25))

    plt.show()
