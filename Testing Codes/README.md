# Testing-Codes

Just a dump of various codes. Ideally one would use a testing branch, but.

# Ideas
Just some thoughts I run into.

Initialization:
* A badass plan:

   initramfs for pi with stored public key of master controller.

   I only got so far to create an x64 initramfs with busybox. Incorporating a python interpreter may prove to be
   difficult

   I heard around the grapevine that initramfs on Pi's may be a touch difficult because they need to initialize the GPU.

* Network:
** Statically defined IPv4 addresses.

   This was how the ROV was setup in the past. We simply used the pre-defined IPv4 link-local address already
   defined on the devices. 169.254.0.0/16 addresses. I'm hesitant to use these because I'm not sure if they always
   exist.

** IPv6

   Use IPv6 link local addresses which are unique for the most part. They are also mandatory.

** DHCP server
   Set up a dhcp server on the controller and communicate to all leases that it hands out. /var/lib/misc/dnsmasq.leases

   I liked this idea until thinking about wireless implications. Tethered multi-ROV systems seem a tad silly.
   Whereas the wireless setup for this will require setting up an access point on the master, connecting each pi
   to the AP so dhcpcd can maybe remember it on boot.

   Now that I write this it's sounding pretty neat. Maybe a custom openWRT image with master code installed!
