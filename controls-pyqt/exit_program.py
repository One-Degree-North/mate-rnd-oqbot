import sys
from comms import Communications

class Exit_Program:
    def __init__(self, comm: Communications):
        self.comms: Communications = comm
        
    def Exit(self):
        self.comms.kill_op()
        sys.exit()
