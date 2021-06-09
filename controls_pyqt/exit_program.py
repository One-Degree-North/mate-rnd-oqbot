import sys
from comms import Communications


class ExitProgram:
    def __init__(self, comm: Communications):
        self.comms: Communications = comm

    def exit(self):
        self.comms.kill_elec_ops()