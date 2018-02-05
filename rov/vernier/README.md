The code expects the GoIO SDK to be installed on the system.
This is available at https://github.com/VernierSoftwareTechnology/GoIO_SDK
Don't forget to enable libusb if you are connecting to the Vernier device through USB!

I've added the libraries compiled on ARM x64 as well as the header files.

The program expects the shared libraries to be in the linker path.

As of right now this is a standalone binary that needs integration with the ROV.
Either we can perform some C calls from python, or we can write a python library.
The former is easier, but the latter has positive implications for the research community as a whole.
