""" Plots a values from the IMU along with a rolling average of the previous N values."""
import collections
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from devices.imu import IMU

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
DATA_POINTS = 150
AVG_COUNT = 30

prev_data_points = collections.deque(maxlen=AVG_COUNT)

def plot_data(label, dataX, dataY, dataZ):
    """ Plot data assuming X is time
        Save the figure
    """
    fig = plt.figure(figsize=(10, 7))
    plt.plot(dataX, dataZ, label="avg")
    plt.plot(dataX, dataY, label="raw")
    plt.xlabel('time(s)')
    plt.ylabel(label)
    #plt.yticks(np.arange(min(accel_data[0]), max(accel_data[0])+1, 0.25))

    plt.legend()
    fig.savefig(label + str(DATA_POINTS) + ".png")

if __name__ == '__main__':
    """ Poll the imu at random intervals and plot stuff.
        The internal poll rate of the firmware is 20ms(50Hz)
        so polling faster than that is pointless
    """
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)

    accel_data = [[], [], []]
    avg_data = []
    time_data = []

    start_time = time.time()
    for i in range(0, DATA_POINTS):
        accel, gyro = imu.read_bin()

        accel_data[0].append(accel[0])
        accel_data[1].append(accel[1])
        accel_data[2].append(accel[2])
        prev_data_points.append(accel)

        if i >= AVG_COUNT:
            avges = [sum(i) / AVG_COUNT for i in zip(*prev_data_points)]
            avg_data.append(list(avges))
        else:
            avg_data.append(accel)

        time_data.append(time.time() - start_time)
        time.sleep(random.random() * 0.1 + 0.1)

    avg_by_axis = [i for i in zip(*avg_data)]
    plot_data('X', time_data, accel_data[0], avg_by_axis[0])
    plot_data('Y', time_data, accel_data[1], avg_by_axis[1])
    plot_data('Z', time_data, accel_data[2], avg_by_axis[2])
