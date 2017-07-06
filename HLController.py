import time
import numpy

# High level controller
class HLController:
    def __init__(self):
        self.goalPos = numpy.zeros(3)
        self.position = numpy.zeros(3)
        self.velocity = numpy.zeros(3)
        self.rotation = numpy.zeros(3)
        self.time = time.time()
        self.pos_time = self.time

    # Given accelerometer data, update position
    def updatePos(self, accel):
        curr_time = time.time()

        self.position += self.velocity
        self.updateVelocity(accel, curr_time)

        self.pos_time

    # Given acceleratometer data and data time, calculate velocity
    def updateVelocity(self, accel, curr_time):
        x, y, z = accel

        delta_time = curr_time - self.pos_time

        self.velocity[0] += x * delta_time;
        self.velocity[1] += y * delta_time;
        self.velocity[2] += z * delta_time;

    # Given gyro data, update rotation
    def updateRot(self, gyro):
        x, y, z = gyro

    def getPos(self):
        return self.position

    def getRot(self):
        return self.rotation
