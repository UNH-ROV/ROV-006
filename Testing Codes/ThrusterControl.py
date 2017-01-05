""" Library to control thrusters.
This needs Adafruit_PWM_Servo_Driver. pip install adafruit-pca9685.
See these links for installation guidelines:
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
https://github.com/adafruit/Adafruit_Python_PCA9685

Initializes PiHat PWM communication then leaves available functions to drive the ROV overall.
The specific signal strengths and thruster activation will have to be catered to each ROV.

Please specify the coordinate system for the ROV.
i.e.
The coordinate system:
    X is forward
    Y is up
    Z is right
"""

import time
import Adafruit_PCA9685

# Thruster pins on the ServoHat
thruster0 = 0;
thruster1 = 2;
thruster2 = 4;
thruster3 = 6;
thruster4 = 8;
thruster5 = 10;
thruster6 = 12;
thruster7 = 14;

# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

# Pulse length of PWM. Add and subtract to this for speeds
# 150 - 600 is a reasonable range for pulse length
servo_center = 307

# Initialize thrusters. Unsure if this is necessary
#hat.setPWM(thruster0, 0, servo_center)
#hat.setPWM(thruster1, 0, servo_center)
#hat.setPWM(thruster2, 0, servo_center)
#hat.setPWM(thruster3, 0, servo_center)
#hat.setPWM(thruster4, 0, servo_center)
#hat.setPWM(thruster5, 0, servo_center)
#hat.setPWM(thruster6, 0, servo_center)
#hat.setPWM(thruster7, 0, servo_center)

def drive(x, y, z)
    """ Move in the specified direction. This is a relative vector. """
    # We'll need to implement this.
    #hat.setPWM(thruster0, 0, center + Value)

def rotate(x, y, z)
    """ Rotate to the given Euler rotation. Fun maths computation ahead :D!
    """
