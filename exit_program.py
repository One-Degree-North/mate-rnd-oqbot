import sys

class Exit_Program:
    def __init__(self, comm):
        self.comms = comm
        
    def exit(self):
        self.comms.kill_op()
        sys.exit()
