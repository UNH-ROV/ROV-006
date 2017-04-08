LIGHT_MAX = 1600
LIGHT_MIN = 400
LIGHT_INC = 200

class Light:
    """Brightness incrementation doesn't work. Our light does not have this feature??? """
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
            self.on = 1
        else:
            self.pwm.set_pwm(self.pin, 0, 0)
            self.on = 0

    def set_on(self):
        self.pwm.set_pwm(self.pin, 0, self.brightness)

    def set_off(self):
        self.pwm.set_pwm(self.pin, 0, 0)

if __name__ == "__main__":
    import time
    import Adafruit_PCA9685

    PWM_FREQ = 48
    LIGHT_PIN = 15

    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(PWM_FREQ) # 50 Hz is good for servo

    light = Light(pwm, LIGHT_PIN)
    light.set_on()
    time.sleep(1)
    light.set_off()
    time.sleep(3)

