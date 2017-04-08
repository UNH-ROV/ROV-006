import serial
import time

ser = serial.Serial()
ser.port = '/dev/ttyUSB0'
ser.baudrate = 57600
ser.open()

# Configure imu to not stream data before running this code.
ser.readline() # Initializes communication to allow the write to work
ser.write(b'#o1')

while True:
    ser.write(b'#f') # Send binary gyro
    line = ser.readline()
    print(line)

    #yaw = float(line[0:4])
    #pitch = float(line[4:8])
    #roll = float(line[8:12])
##
    #print("%f, %f, %f" % (yaw, pitch, roll))
