# ROV
This program contains all the logic for controller the ROV.
It listens for controller information and reacts accordingly by
driving thrusters and activating lights and sensors.

## Dependencies
* python3-pip

## Setup on a Pi
It is expected that you are located in this directory.
* Enable I2C for Pi, likely using `raspi-config`
* `pip install .`
* `rov-control` or `./rov.py`
* Modify the following constants based on how you've configured your hardware:
  * LIGHT_PIN at the top of `rov.py`
  * THRUSTER_PINS at the top of `devices/t100.py`

## Additional Technical Notes
Raspbian's latest repositories seem to have Python3.4 by default.
Rather than be sensible and install a functional version, I've instead opted to use old syntax.
To update to Python 3.5+, one can replace a couple of the old asyncio keywords:
Replace `@asyncio.coroutine` with `async`. Replace `yield from` with `await`.
