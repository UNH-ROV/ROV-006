# Station
This program attempts to connect to a devices located at a particular IP
address and port. It then consistently sends state information to said device.

## High level controller
The station syncs desired parameters for high level controllers such as PID and LQR with the ROV.
These are optionally accessible by installing the necessary GUI dependencies.
If these GUI dependencies are not installed, controller constants are not sent.

## Dependencies
* python3-pip
* xboxdrv
* gtk3 (optional)
* python-gobject2 (optional)
* gobject-introspection (optional)

## Setup
* `pip install .`

The xbox driver code is directly copied from a repo I made for it: [https://github.com/Meptl/xbox-async].
