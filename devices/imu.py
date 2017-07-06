import serial
import struct
import time

SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_BAUD = 57600
WRITE_WAIT = 0.01

class IMU(serial.Serial):
    def __init__(self, dev, rate):
        serial.Serial.__init__(self, dev, rate)
        time.sleep(3)

        #self.write(b'#o0#ob')
        self.write(b'#o0#oscb')
        self.flush()
        time.sleep(WRITE_WAIT) # Wait for write

    def get_sensors(self):
        """ Expects the IMU to be configured to output all sensor data. """
        self.flushOutput() # Clear whatever garbage may have been on the line
        self.flushInput()

        self.write(b'#f')
        self.flush()
        time.sleep(0.01) # Wait for write

        line = self.read(WRITE_WAIT)

        accelX = struct.unpack('f', line[0:4])[0]
        accelY = struct.unpack('f', line[4:8])[0]
        accelZ = struct.unpack('f', line[8:12])[0]
        magX = struct.unpack('f', line[12:16])[0]
        magY = struct.unpack('f', line[16:20])[0]
        magZ = struct.unpack('f', line[20:24])[0]
        gyroX = struct.unpack('f', line[24:28])[0]
        gyroY = struct.unpack('f', line[28:32])[0]
        gyroZ = struct.unpack('f', line[32:36])[0]

        return (accelX, accelY, accelZ), (magX, magY, magZ), (gyroX, gyroY, gyroZ)

if __name__ == '__main__':
    imu = IMU(SERIAL_DEV, SERIAL_BAUD)
    accel, mag, gyro = imu.get_sensors()
    print("ACC:", accel[0], accel[1], accel[2])
    print("MAG:", mag)
    print("GYRO:", gyro)
