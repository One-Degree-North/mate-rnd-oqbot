import sys


class Exit_Program:
    def __init__(self, comm: Communications, mcu: MCUInterface):
        self.comms: Communications = comm
        self.mcu: MCUInterface = mcu
        
    def Exit(self):
        self.comms.kill_op()
        self.mcu.close_serial()
        sys.exit()
