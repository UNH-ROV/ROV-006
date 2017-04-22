LIGHT_MAX = 1600
LIGHT_MIN = 400
LIGHT_INC = 400

class Light:
    def __init__(self, pwm, pin):
        self.pwm = pwm
        self.pin = pin
        self.brighness = 800
        self.on = 0

    def set_servo_pulse(self, channel, pulse):
        pulseLength = 1000000
        pulseLength /= 60
        #print "%d us per period" % pulseLength
        pulseLength /= 4096
        print "%d us per bit" % pulseLength
        pulse *= 1000
        pulse /= pulseLength
        pwm.setPWM(channel, 0, pulse)

    def inc_brightness(self):
        self.brightness += LIGHT_INC
        if self.brightness > LIGHT_MAX
            self.brightness = LIGHT_MAX

    def dec_brightness(self):
        self.brightness -= LIGHT_INC
        if self.brightness < LIGHT_MIN
            self.brightness = LIGHT_MIN

    def toggle_light(self):
        if not self.on:
            pwm.set_pwm(self.pin, 0, self.brightness)
        else:
            pwm.set_pwm(self.pin, 0, 0)
