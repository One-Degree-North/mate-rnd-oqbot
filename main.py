import sys
import comms
sys.path.insert(0, './controls-pyqt')
import exit_program
import gui
sys.path.insert(0, './mcu-lib')
import mcu
from PyQt5.QtWidgets import QApplication

BAUD_RATE: int = 230400
CLOSE_ON_STARTUP: bool = True
MAX_READ: int = 16
PORT: str = "/dev/ttyUSB0"
REFRESH_RATE: int = 1440
	
INITIAL_PERCENTAGE: int = 100
SENSITIVE_PERCENTAGE: int = 50

def start():
	app = QApplication(sys.argv)
	feather = mcu.MCUInterface(PORT,
                               baud = BAUD_RATE,
                               close_on_startup = CLOSE_ON_STARTUP,
                               refresh_rate = REFRESH_RATE,
                               max_read = MAX_READ)
	communications = comms.Communications(feather, SENSITIVE_PERCENTAGE, INITIAL_PERCENTAGE)
	exit = exit_program.Exit_Program(communications)
	window2 = gui.MainWindow(feather, communications, exit)
	window2.setup_ui()
	sys.exit(app.exec_())

start()
