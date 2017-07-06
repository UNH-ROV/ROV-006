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

class PID:
    """ PID controller
    """
    def __init__(self, p=2.0, i=0.5, d=1.0, integral=0, integral_max=500, integral_min=-500):
        self.kP = p
        self.kI = i
        self.kD = d
        self.integral = integral
        self.integral_max = integral_max
        self.integral_min = integral_min

        self.prev_error = numpy.zeros(3)
        self.goal = numpy.zeros(3)

    def update(self, current_value, delta_time):
        """ Calculate PID output value for given reference input and feedback
        """
        error = self.goal - current_value

        p = self.Kp * self.error

        self.integral += self.integral + self.error
        self.integral = clamp(self.integral, self.integral_min, self.integral_max)
        i = self.integral * self.kI

        d = self.kD * (error - self.prev_error) / delta_time

        self.prev_error = error

        return p + i + d

    def reset(self):
        self.integral = 0.0
        self.prev_error = numpy.zeros(3)

    def clamp(i, clamp_min, clamp_max):
        """ Clamp i between min and max
        """
        return max(clamp_min, min(i, clamp_max))
