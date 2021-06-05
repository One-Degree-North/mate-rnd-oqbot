import comms
import exit_program
import gui
import mcu


BAUD_RATE: int = 230400
CLOSE_ON_STARTUP: bool = True
MAX_READ: int = 16
PORT: str = "/dev/ttyACM0"
REFRESH_RATE: int = 1440

def start():
	feather = mcu.MCUInterface(PORT,
                               baud: int = BAUD_RATE,
                               close_on_startup: bool = CLOSE_ON_STARTUP,
                               refresh_rate: int = REFRESH_RATE,
                               max_read: int = MAX_READ)
	communications = comms.Communications(feather)
	exit = exit_program.ExitProgram(communications)
	window2 = gui.MainWindow(feather, communications, exit)
	window2.setup_ui()

start()
