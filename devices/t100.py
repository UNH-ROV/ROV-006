""" Library to control thrusters.
This needs Adafruit_PWM_Servo_Driver. pip install adafruit-pca9685.
See these links for installation guidelines:
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
https://github.com/adafruit/Adafruit_Python_PCA9685

Pinouts also need to be specified per ROV.
The specific signal strengths and thruster activation will have to be catered to each ROV.

The class initializes PiHat PWM communication. It has available functions that modify
how much power it will put into the thrusters.
Once this is done, the drive() function will send signals to the thrusters.

"""

import time
import numpy as np

THRUSTER_PINS = [2, 3, 4, 5, 8, 9, 10, 13]
NUM_THRUSTERS = len(THRUSTER_PINS)
MAX_POWER = 40
PWM_FREQ = 48

# Pulse length of PWM. Add and subtract to this for speeds.
# There are performance graphs online
# 307 / 1024 ticks (Pi hat) = 1500 us PWM
SERVO_CENTER = 307

# These weights dictate which thrusters get turned on when we want to apply the particular vector
WEIGHTS_BIAS       = np.array([-1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0], float)
WEIGHTS_FORWARD    = np.array([1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0], float)   # positive forward
WEIGHTS_HORIZONTAL = np.array([1.0, -1.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0], float) # positive right
WEIGHTS_VERTICAL   = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0], float)   # positive up
WEIGHTS_PITCH      = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0, -1.0, -1.0], float) # positive tips up
WEIGHTS_YAW        = np.array([-1.0, 1.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0], float) # positive ccw
WEIGHTS_ROLL       = np.array([0.0, 0.0, 1.0, -1.0, 0.0, 0.0, -1.0, 1.0], float)   # positive ccw

#WEIGHT_MIN = 0.05


class Thrusters:
    def __init__(self, pwm):
        self.pwm = pwm

        # Initialize thrusters. Unsure if this is necessary
        for i in range(0, NUM_THRUSTERS):
            self.pwm.set_pwm(THRUSTER_PINS[i], 0, SERVO_CENTER)

        # This is the resulting weight from all vectors
        self.weights_forward    = np.zeros(NUM_THRUSTERS)
        self.weights_horizontal = np.zeros(NUM_THRUSTERS)
        self.weights_vertical   = np.zeros(NUM_THRUSTERS)
        self.weights_pitch      = np.zeros(NUM_THRUSTERS)
        self.weights_yaw        = np.zeros(NUM_THRUSTERS)
        self.weights_roll       = np.zeros(NUM_THRUSTERS)

    def move_forward(self, scalar):
        """ Scale weights to move forward. percent should range from -1 to 1"""
        self.weights_forward = scalar * WEIGHTS_FORWARD

    def move_horizontal(self, scalar):
        """ Scale weights to move horizontally. Scalar should range from -1 to 1."""
        self.weights_horizontal = scalar * WEIGHTS_HORIZONTAL

    # Positive is up.
    def move_vertical(self, scalar):
        """ Scale weights to move vertical. Scalar should range from -1 to 1."""
        self.weights_vertical = scalar * WEIGHTS_VERTICAL

    def move_pitch(self, scalar):
        """ Scale weights to move pitch. Scalar should range from -1 to 1."""
        self.weights_pitch = scalar * WEIGHTS_PITCH

    def move_yaw(self, scalar):
        """ Scale weights to move yaw. Scalar should range from -1 to 1."""
        self.weights_yaw = scalar * WEIGHTS_YAW

    def move_roll(self, scalar):
        """ Scale weights to move roll. Scalar should range from -1 to 1."""
        self.weights_roll = scalar * WEIGHTS_ROLL

    def clear_weights(self):
        for i in range(0, NUM_THRUSTERS):
            self.weights_forward[i] = 0
            self.weights_horizontal[i] = 0
            self.weights_vertical[i] = 0
            self.weights_pitch[i] = 0
            self.weights_yaw[i] = 0
            self.weights_roll[i] = 0

    def stop(self):
        for i in range(0, NUM_THRUSTERS):
            self.pwm.set_pwm(THRUSTER_PINS[i], 0, SERVO_CENTER)

    def drive(self):
        """ Send PWM signal to thrusters.
            Sum the weight vectors of each direction of interest to get weights for the resulting vector.

        """
        weights_sum = self.weights_forward + self.weights_horizontal + self.weights_vertical + self.weights_pitch + self.weights_yaw + self.weights_roll
        #for i in range(0, NUM_THRUSTERS):
            #if weights_sum[i] < WEIGHT_MIN:
                #weights_sum[i] = 0

        print(weights_sum)

        # Sign mod
        weights_sum *= WEIGHTS_BIAS

        # Normalize the sum so the next step doesn't generate PWM signals beyond our desired range.
        max_weight = weights_sum.max()
        if max_weight > 1.0:
            weights_sum /= max_weight

        weights_sum *= MAX_POWER

        for i in range(0, NUM_THRUSTERS):
            signal = int(SERVO_CENTER + weights_sum[i])

            # Test this before sending it out. wouldn't want to fry anything (If that's even possible).
            #print("Thruster %d gets %d" % (i, signal))
            self.pwm.set_pwm(THRUSTER_PINS[i], 0, signal)

        #self.clear_weights()

    def set_pwm(self, pin, channel, value):
        """ Send PWM signal directly to thrusters. Used for debugging. """
        self.pwm.set_pwm(pin, channel, value)

import signal
import sys
import Adafruit_PCA9685
if __name__ == '__main__':
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo
    thrust = Thrusters(pwm)
    time.sleep(3)
    #thrust.move_vertical(1.0)
    #thrust.drive()
    #time.sleep(8)
    #thrust.stop()
