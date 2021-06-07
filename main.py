import comms
import exit_program
import gui
import mcu


BAUD_RATE: int = 230400
CLOSE_ON_STARTUP: bool = True
MAX_READ: int = 16
PORT: str = "/dev/ttyACM0"
REFRESH_RATE: int = 1440
	
INITIAL_PERCENTAGE: int = 100
SENSITIVE_PERCENTAGE: int = 50

def start():
	feather = mcu.MCUInterface(PORT,
                               baud = BAUD_RATE,
                               close_on_startup = CLOSE_ON_STARTUP,
                               refresh_rate = REFRESH_RATE,
                               max_read = MAX_READ)
	communications = comms.Communications(feather, SENSITIVE_PERCENTAGE, INITIAL_PERCENTAGE)
	exit = exit_program.ExitProgram(communications)
	window2 = gui.MainWindow(feather, communications, exit)
	window2.setup_ui()

start()
