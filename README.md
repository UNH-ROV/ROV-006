# ROV-006
This program drives 8 thrusters, a light, a pressure sensor, a salinity sensor, and two cameras, using a Raspberry Pi 3 and a PWM PiHat.
One would have to modify the IP address constants at the top of the client and server program to use this elsewhere.
Currently the ROV's IP is 192.168.0.15 while the station IP is 192.168.0.14.

The Raspberry Pi 3 uses Python3.4. As a result, the code in the ROV program uses the older asyncio syntax.
To update to Python 3.5+, one can replace a couple of the old asyncio keywords.
Replace `@asyncio.coroutine` with `async`. Replace `yield` from with `await`.

* gtk3
* python-gobject2
* gobject-introspection
* gbulb

Academic Year 2016-2017
