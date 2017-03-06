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
import Adafruit_PCA9685

NUM_THRUSTERS = 8

# These weights dictate which thrusters get turned on when we want to apply the particular vector
WEIGHTS_FORWARD    = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)
WEIGHTS_HORIZONTAL = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)
WEIGHTS_VERTICAL   = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)
WEIGHTS_PITCH      = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)
WEIGHTS_YAW        = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)
WEIGHTS_ROLL       = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float)

# Thruster pins on the ServoHat
thrusters = [0, 2, 4, 6, 8, 10, 12, 14];



# Pulse length of PWM. Add and subtract to this for speeds.
# 150 - 600 is a reasonable range for pulse length.
# There are performance graphs online for my purposes I'll use a logarithmic scale.
servo_center = 307

class Thrusters:
    def __init__(self):
        # Initialise the PCA9685 using the default address (0x40).
        pwm = Adafruit_PCA9685.PCA9685()

        # Set frequency to 60hz, good for servos.
        pwm.set_pwm_freq(60)

        # Initialize thrusters. Unsure if this is necessary
        #for i in range(0, 8):
            #hat.setPWM(thruster[i], 0, servo_center)

        # This is the resulting weight from all vectors
        self.weights_forward    = np.zeros(NUM_THRUSTERS)
        self.weights_horizontal = np.zeros(NUM_THRUSTERS)
        self.weights_vertical   = np.zeros(NUM_THRUSTERS)
        self.weights_pitch      = np.zeros(NUM_THRUSTERS)
        self.weights_yaw        = np.zeros(NUM_THRUSTERS)
        self.weights_roll       = np.zeros(NUM_THRUSTERS)

        return self

    def move_forward(self, scalar):
        """ Scale weights to move forward. percent should range from -1 to 1"""
        self.weights_forward = scalar * WEIGHTS_FORWARD

    def move_horizontal(self, scalar):
        """ Scale weights to move horizontally. Scalar should range from -1 to 1."""
        self.weights_horizontal = scalar * WEIGHTS_HORIZONTAL

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

    def drive():
        """ Send PWM signal to thrusters.
            Sum the weight vectors of each direction of interest to get weights for the resulting vector.
            Exponentiation causes the following weight results: -1=150, 1=600.
        """
        weights_result = self.weights_forward + self.weights_horizontal + self.weights_vertical + \
                         self.weights_pitch + self.weights_yaw + self.weights_roll

        # Normalize the resultant so the next step doesn't generate PWM signals beyond our desired range.
        weights_result = weights_result / weights_result.max()

        print("Sending values to thrusters: %s", weights_result)

        for i in range(0, NUM_THRUSTERS):
            # Test this before sending it out. wouldn't want to fry anything (If that's even possible).
            print("Thruster %d gets %f" % i, servo_center * (2 ** weights_results[i]))
            #hat.setPWM(thruster[i], 0, servo_center * (2 ** weights_results[i]))
