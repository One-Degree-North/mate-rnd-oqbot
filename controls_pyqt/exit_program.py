import sys
from comms import Communications


class ExitProgram:
    def __init__(self, comm: Communications):
        self.comms = comm
        
    def Exit(self):
        self.comms.kill_elec_ops()
        sys.exit()
