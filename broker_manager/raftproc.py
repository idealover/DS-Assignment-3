# Spawn a raft process and wait for it to exit.
#
# Args:
#     port: the port on which the process will listen for connections
#     broker: the port of the broker
#     peers: a list of ports of the peers
#     log_file: the file to which the process will write its log

# take the arguments from the command line
# log_file is optional

import sys
import os

# import the raft process class
from raftProcClass import raftProc

if len(sys.argv) < 2:
    print('Usage: python raftproc.py port broker peers [log_file]')
    sys.exit(1)

# get the arguments
port = int(sys.argv[1])
broker = int(sys.argv[2])

# add the current directory to the path
sys.path.append(os.getcwd())

raft_proc = raftProc(port, port, broker)
