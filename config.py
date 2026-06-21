"""
config.py

Central place to set the target IP and port range. Keeping this
separate from main.py means changing what you're scanning doesn't
require touching the program logic at all -- you just edit this file.

Author: Michael
Course: CYB 333
"""

# The VM (or any host) this tool monitors. Update this to match your
# own VirtualBox host-only network IP -- find it by running `ip a`
# inside the target VM and looking for the 192.168.56.x address.
TARGET_IP = "192.168.56.101"

# Full well-known port range. Scanning this whole range (rather than
# just a handful of known ports) means the tool can catch ANY
# unexpected port that opens, not just ones we already know to check.
START_PORT = 1
END_PORT = 1024
