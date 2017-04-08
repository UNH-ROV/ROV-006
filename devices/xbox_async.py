""" Controller support using asyncio.
Handlers for digital buttons occur twice per button press.
Analog signals are called whenever events occur.
"""
import asyncio
from enum import Enum

class Button(Enum):
    """ Enum for controller events. Values are arbitrary but unique. """
    A, B, X, Y = range(0, 4)
    LStick, RStick, LTrigger, RTrigger = range(4, 8)
    L3, R3, LB, RB = range(8, 12)
    DpadU, DpadD, DpadL, DpadR = range(12, 16)
    Back = 16
    Start = 17
    Guide = 18   # This is the Xbox button on the Xbox controller

class Joystick:
    @classmethod
    async def create(cls,
                     args=["--no-uinput", "--detach-kernel-driver"],
                     deadzone=4000,
                     normalize=False):
        """ Spawns xboxdrv using the given arguments. This is useful for telling xboxdrv to work with
        a second controller, or a specific device.
        """
        self = Joystick()
        self.deadzone = deadzone
        self.normalize = normalize
        self.proc = await asyncio.create_subprocess_exec("xboxdrv",
                                                         *args,
                                                         stdout=asyncio.subprocess.PIPE)

        # Init callback dict
        self.handlers = {}
        for b in Button:
            self.handlers[b] = []

        # Evaluate xboxdrv preample.
        # This could likely use some improvement
        while True:
            line = await self.proc.stdout.readline()
            if line:
                if b'Press' in line:
                    break
                if b'ERROR' in line:
                    error_msg = await self.proc.stdout.readline() # Next line is error message
                    raise OSError(error_msg.decode())
            else:
                raise RuntimeError('Failed to read xboxdrv')

        return self


    async def read(self):
        line = await self.proc.stdout.readline()
        if line:
            self.call_handlers(line)

        return self

    def on_button(self, button, callback):
        self.handlers[button].append(callback)

    def call_handlers(self, line):
        """ Each handler will parse its portion of the input line """
        self.handle_stick_l(line)
        self.handle_stick_r(line)
        self.handle_dpad(line)
        self.handle_special(line)
        self.handle_action_buttons(line)
        self.handle_bumpers(line)
        self.handle_triggers(line)

    def handle_stick_l(self, line):
        """ Returns a value from (-32768 to +32767) or (-1 to 1) if normalize=True
        Stick handlers are called for every input of the controller unless the stick is in the deadzone.
        If the LStick is outside the deadzone and A is pressed, LStick handlers will be called.
        """
        if self.handlers[Button.LStick]:
            leftX = int(line[3:9])
            leftY = int(line[13:19])

            # if value is beyond deadzone, do stuff
            if not(abs(leftX) < self.deadzone and abs(leftY) < self.deadzone):
                if self.normalize:
                    leftX /= 32768.0
                    leftY /= 32768.0

                for cb in self.handlers[Button.LStick]:
                    cb(leftX, leftY)

        # "Clicking" the left analog stick
        if self.handlers[Button.L3] and int(line[90:91]):
            for cb in self.handlers[Button.L3]:
                cb()

    def handle_stick_r(self, line):
        """ Returns a value from (-32768 to +32767) or (-1 to 1) if normalize=True
        Stick handlers are called for every input of the controller unless the stick is in the deadzone.
        If the LStick is outside the deadzone and A is pressed, LStick handlers will be called.
        """
        if self.handlers[Button.RStick]:
            rightX = int(line[24:30])
            rightY = int(line[34:40])

            # if value is beyond deadzone, do stuff
            if not(abs(rightX) < self.deadzone and abs(rightY) < self.deadzone):
                if self.normalize:
                    rightX /= 32768.0
                    rightY /= 32768.0

                for cb in self.handlers[Button.RStick]:
                    cb(rightX, rightY)

        # "Clicking" the left analog stick
        if self.handlers[Button.R3] and int(line[95:96]):
            for cb in self.handlers[Button.R3]:
                cb()

    def handle_dpad(self, line):
        if self.handlers[Button.DpadU] and int(line[45:46]):
            for cb in self.handlers[Button.DpadU]:
                cb()

        if self.handlers[Button.DpadD] and int(line[50:51]):
            for cb in self.handlers[Button.DpadD]:
                cb()

        if self.handlers[Button.DpadL] and int(line[55:56]):
            for cb in self.handlers[Button.DpadL]:
                cb()

        if self.handlers[Button.DpadR] and int(line[60:61]):
            for cb in self.handlers[Button.DpadR]:
                cb()

    def handle_special(self, line):
        if self.handlers[Button.Back] and int(line[68:69]):
            for cb in self.handlers[Button.Back]:
                cb()

        if self.handlers[Button.Guide] and int(line[76:77]):
            for cb in self.handlers[Button.Guide]:
                cb()

        if self.handlers[Button.Start] and int(line[84:85]):
            for cb in self.handlers[Button.Start]:
                cb()

    def handle_action_buttons(self, line):
        if self.handlers[Button.A] and int(line[100:101]):
            for cb in self.handlers[Button.A]:
                cb()

        if self.handlers[Button.B] and int(line[104:105]):
            for cb in self.handlers[Button.B]:
                cb()
        if self.handlers[Button.X] and int(line[108:109]):
            for cb in self.handlers[Button.X]:
                cb()
        if self.handlers[Button.Y] and int(line[112:113]):
            for cb in self.handlers[Button.Y]:
                cb()

    def handle_bumpers(self, line):
        if self.handlers[Button.LB] and int(line[118:119]):
            for cb in self.handlers[Button.LB]:
                cb()

        if self.handlers[Button.RB] and int(line[123:124]):
            for cb in self.handlers[Button.RB]:
                cb()

    def handle_triggers(self, line):
        """ Returns a value from 0 - 255 or 0 - 1 if normalize=True"""
        if self.handlers[Button.LTrigger]:
            for cb in self.handlers[Button.LTrigger]:
                val = int(line[129:132])
                if self.normalize:
                    val /= 255.0
                cb(val)

        if self.handlers[Button.RTrigger]:
            for cb in self.handlers[Button.RTrigger]:
                val = int(line[136:139])
                if self.normalize:
                    val /= 255.0
                cb(val)

    def close(self):
        self.proc.kill()
