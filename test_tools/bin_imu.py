import serial
import struct
import time
import math

"""
  "#s<xy>" - Request synch token - useful to find out where the frame boundaries are in a continuous
         binary stream or to see if tracker is present and answering. The tracker will send
     "#SYNCH<xy>\r\n" in response (so it's possible to read using a readLine() function).
     x and y are two mandatory but arbitrary bytes that can be used to find out which request
     the answer belongs to.
"""
SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600

ser = serial.Serial(SERIAL_DEV, SERIAL_BAUD)
time.sleep(3)
ser.write(b'#o0#oscb#sab')
ser.flush()
time.sleep(1)

while True:
    line = ser.readline();
    if line.endswith("#SYNCHab\r\n"):
        break

while True:
    ser.write(b'#f')
    ser.flush()

    line = ser.read(32)
    word = struct.unpack('fff', line[24:36])
    yaw = word[0]
    roll = word[1]
    pitch = word[2]
    """
    yaw = struct.unpack('f', line[0:4])[0]
    roll = struct.unpack('f', line[4:8])[0]
    pitch = struct.unpack('f', line[8:12])[0]
    """

    print("Y: {}, R: {}, P: {}".format(yaw, roll, pitch))
    time.sleep(0.2)
