# ROV-006
This repository houses two projects:
ROV control code located in the `rov` directory and surface station code located in the `station` directory.
Note that "station" refers to the device which will control the ROV.
At the time of writing, this is just a laptop with an xbox controller attached.

## Starting from scratch
Each project has instructions on how to get it up and running.
The communication between the ROV and the station are statically defined.

The ROV is assigned the IP address: 192.168.0.15.

The station is assigned the IP address: 192.168.0.14.

They communicate on UDP and TCP ports 30002.

To modify these values to your environment, modify the constants defined at the top of `rov.py` and `station.py`.
Each project should direct you on other things to be modified.

### Quality of Life Customizations
These are customizations that are not necessary, but I have setup to make life easier.
* Created a startup script to run the rov-control on boot
* Statically configured the IP address on the station
* Statically configured the IP address on the ROV
* Added a udev rule to make the Xbox controller accessible by non-root users.

## Magic Runbooks
I did a lot of interesting things to work with the pi whilst it was in the ROV.
I trust if you are confident enough to run these, I won't have to spoon feed the details.

## Internet for the Pi
I forwarded the ethernet traffic from the Pi through the station's Wifi card.
Note that I only configured the IP for the Pi which is why I have to add some networking configuration to get internet.

1. ROV: `ip route add default via 192.168.0.14` Create a default route to the station from the pi.
2. ROV: `sudo bash -c 'echo nameserver 8.8.8.8 >> /etc/resolv.conf` Add dns server on pi.
3. Station: `sysctl -w net.ipv4.ip_forward=1` Configure station to forward traffic.
4. Station: `iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE` Create a firewall rule to forward data to the wifi interface.

After this you should be free to update the ROV, and push/pull code from github.

## Working with USB devices on the Pi.
To reflash the firmware on the IMU, I was able to X forward Arduino.
`ssh -X pi@192.168.0.15`

I also had to run Processing to calibrate the magnetometer.
This program actually exceeded the graphical capacity for the pi.
To solve this I forwarded the USB devices through ethernet using usbip.
And worked with the USB devices on the station.
This might be useful in the future to eliminate the need for a second ethernet USB extender that accesses the camera.
usbip has moved around a bit so it's hard for me to describe this process.
For the most part usbip should be available in the linux-generic-tools package which will simply add an executable at /usr/lib/linux-tools/$(uname -r)/usbip.
See the man pages for usage.

These are the steps I took. They likely WON'T apply to other systems due to major changes between versions of usbip.
1. ROV: `uspipd` Start usbipd (I'm sorry)
2. ROV: `usbip list -l` List usb devices.
3. ROV: `usbip bind -b <busid>` Choose a device from the list and bind usb device.
4. Station: `modprobe vhci-hcd`
5. Station: `/usr/lib/linux-tools/$(uname -r)/usbip attach -r 192.168.0.15 -b 1-1.5` Mount the usb.

## Running station as non-root user
Adds a udev rule that allows users in the input group to access usb devices

`/etc/udev/rules.d/99-xbox.rules`

`SUBSYSTEM=='usb',GROUP='input',MODE='0666'`

## Additional Technical Notes
### DHCP
Life would actually be quite easier if you configured a DHCP server on the laptop and give the Pi its desired IP address.
I have actually done it and it made networking setup for it quite nice.
I did not employ it in its entirety because I was not sure how lease times and ROV reboots would effect functionality and I did not have the time to test.

## Windows
The station program was only tested in a Linux environment.
Here are a few modifications it will need to work in a Windows environment:
* init windows event loop for asyncio
* Replace xboxdrv with Windows driver and modify the relevant output loops
Despite this I'm still not certain whether it can be used on that platform...

