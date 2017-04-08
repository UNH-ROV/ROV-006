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
ser.write(b'#o0#osct#sab')
ser.flush()
time.sleep(1)

while True:
    line = ser.readline();
    if line.endswith("#SYNCHab\r\n"):
        break

while True:
    ser.write(b'#f')
    ser.flush()

    line = ser.readline()

    if line.startswith("#G"):
        print(line)
