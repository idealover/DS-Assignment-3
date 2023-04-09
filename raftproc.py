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

if len(sys.argv) < 4:
    print('Usage: python raftproc.py port broker peers [log_file]')
    sys.exit(1)

# get the arguments
port = int(sys.argv[1])
broker = int(sys.argv[2])
peers = [int(p) for p in sys.argv[3].split(',')]
if len(sys.argv) == 5:
    log_file = sys.argv[4]
else:
    log_file = None

# add the current directory to the path
sys.path.append(os.getcwd())

# import the raft process class
from raftprocClass import RaftProc

# spawn the process
# redirect the output to the log file
if log_file is not None:
    with open(log_file, 'w') as f:
        sys.stdout = f
        sys.stderr = f
        raft_proc = RaftProc(port, port, peers, broker)
else:
    raft_proc = RaftProc(port, port, peers, broker)
