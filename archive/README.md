# Testing-Codes

Just a dump of various codes. Ideally one would use a testing branch, but.

# Thoughts and Ideas
Just some thoughts I run into.

In so far I've used asyncio. I'm sure future ROV developers will curse me for it.

* A badass initialization plan:

    initramfs for pi with stored public key of master controller.

    I only got so far to create an x64 initramfs with busybox. Incorporating a python interpreter may prove to be difficult

    I heard around the grapevine that initramfs on Pi's may be a touch difficult because they need to initialize the GPU.

* Network:
    * Statically defined IPv4 addresses.

    This was how the ROV was setup in the past. We simply used the pre-defined IPv4 link-local address already
    on the devices. 169.254.0.0/16 addresses. I'm hesitant to use these because I'm not sure if they always
    exist.

    * IPv6

    Use IPv6 link local addresses which are unique for the most part. They are also mandatory.

    * DHCP server

    Set up a dhcp server on the controller and communicate to all leases that it hands out. /var/lib/misc/dnsmasq.leases

    I liked this idea until thinking about wireless implications. Tethered multi-ROV systems seem a tad silly.
    Whereas the wireless setup for this will require setting up an access point on the master, connecting each pi
    to the AP so dhcpcd can maybe remember it on boot.

    Now that I write this it's sounding pretty neat. Maybe a custom openWRT image with master code installed!

And then I realized that the end system is too unknown to establish a concrete system and decided to statically configure IPv4 addresses.

* Communication
    I am transmitting controller states using JSON packets over UDP.
    I fear this may be a bit data heavy for simple state matching.

    A simpler, though less sane option would be to send a byte array per packet.

    Interestingly EtherNet/IP may be applicable, but I don't know if you can implement this protocol using off the shelf hardware.

    This may be an application for gRPC, although implementing that would be a touch overkill.

