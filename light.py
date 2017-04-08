LIGHT_MAX = 1600
LIGHT_MIN = 400
LIGHT_INC = 400

class Light:
    def __init__(self, pwm, pin):
        self.pwm = pwm
        self.pin = pin
        self.brightness = 800
        self.on = 0

    def inc_brightness(self):
        self.brightness += LIGHT_INC
        if self.brightness > LIGHT_MAX:
            self.brightness = LIGHT_MAX

    def dec_brightness(self):
        self.brightness -= LIGHT_INC
        if self.brightness < LIGHT_MIN:
            self.brightness = LIGHT_MIN

    def toggle(self):
        if not self.on:
            self.pwm.set_pwm(self.pin, 0, self.brightness)
        else:
            self.pwm.set_pwm(self.pin, 0, 0)

    def set_on(self):
        self.pwm.set_pwm(self.pin, 0, self.brightness)

    def set_off(self):
        self.pwm.set_pwm(self.pin, 0, 0)
