# ROV-006
This program drives 8 thrusters, a light, a pressure sensor, a salinity sensor, and two cameras, using a Raspberry Pi 3 and a PWM PiHat.
The station program was only tested in a Linux environment.
Here are a few modifications it will need to work in a Windows environment:
* init windows event loop for asyncio
* Replace xboxdrv with Windows driver and modify the relevant output loops

## Usage Notes
Simply run the executables. In the terminal: `./rov.py` on the ROV and `./station.py` for the station.
The station program should be run with root privileges because xboxdrv runs as a kernel module. Or you can modify udev.
Currently the ROV's IP is 192.168.0.15 while the station IP is 192.168.0.14.
One would have to modify the IP address constants at the top of the rov and station program to use other addresses.
The ROV listens on port 30002 this is also a constant in rov.py
The pin locations for many of the devices should also be changed should this be mibrated to another environment. These are also defined as constants in many of the files.

# Dependencies
* xboxdrv
* gtk3
* python-gobject2
* gobject-introspection
## Python Packages
* gbulb
* adafruit-pca9685
* And others!

# Additional Technical Notes
The Raspberry Pi 3 uses Python3.4. As a result, the code in the ROV program uses the older asyncio syntax.
To update to Python 3.5+, one can replace a couple of the old asyncio keywords:
Replace `@asyncio.coroutine` with `async`. Replace `yield from` with `await`.

I did a lot of interesting things to work with the pi whilst it was in the ROV.
Assume all the commands below require root privileges so prepend `sudo` if you get a permission denied error.
I'll place the commands here in case someone needs to accomplish these things.
## Internet for the Pi
I made the station a forwarder for ROV traffic.
1. `ip route add default via 192.168.0.14` Create a default route to the station from the pi.
2. `sudo bash -c 'echo nameserver 8.8.8.8 >> /etc/resolv.conf` Add dns server on pi
3. `sysctl -w net.ipv4.ip_forward=1` Configure station to forward traffic
4. `iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE` Create a firewall rule to forward data to the wifi interface

After this you should be free to update the ROV, and push/pull code from github.

## Working with USB devices on the Pi.
To reflash the firmware on the IMU I was able to X forward Arduino.
Simply add the `-X` flag to ssh and run your GUI program from the commandline.
`ssh -X pi@192.168.0.15`

I also had to run Processing to calibrate the magnetometer.
This program actually exceeded the graphical capacity for the pi.
To solve this I forwarded the USB devices through ethernet using usbip.
And worked with the USB devices on the station.
This might be useful in the future to eliminate the need for a second ethernet USB extender that accesses the camera.
usbip has moved around a bit so it's hard for me to describe this process.
For the most part usbip should be available in the linux-generic-tools package which will simply add an executable at /usr/lib/linux-tools/$(uname -r)/usbip.
See the man pages for usage.

These are the steps I took. They likely WON'T apply to other systems.
1. `uspipd` On ROV, start usbipd (I'm sorry)
2. `usbip list -l` On ROV, list usb devices
3. `usbip bind -b <busid>` On ROV, choose a device from the list and bind usb device.
4. `modprobe vhci-hcd` On station
5. `/usr/lib/linux-tools/$(uname -r)/usbip attach -r 192.168.0.15 -b 1-1.5` On station, mount the usb
