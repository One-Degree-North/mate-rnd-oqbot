from __future__ import division, print_function
import sys
import comms
from controls_pyqt import gui, exit_program
from mcu_lib import mcu
from serial.tools import list_ports
from PyQt5.QtWidgets import QApplication
from vpython import *
from visual import Visualizer
from movement import Movement


BAUD_RATE: int = 230400
CLOSE_ON_STARTUP: bool = True
MAX_READ: int = 16

port_list = list_ports.comports()
if not port_list:
    print("No available tty/COM ports. Halting!")
    exit()
port_list = [x.device for x in port_list]
print(f"List of available tty/COM ports: {port_list}")
PORT: str = input("Port to use: ")

REFRESH_RATE: int = 1440

INITIAL_PERCENTAGE: int = 25
SENSITIVE_PERCENTAGE: int = 15


def start():
    feather = mcu.MCUInterface(PORT,
                               baud=BAUD_RATE,
                               close_on_startup=CLOSE_ON_STARTUP,
                               refresh_rate=REFRESH_RATE,
                               max_read=MAX_READ)
    communications = comms.Communications(feather, SENSITIVE_PERCENTAGE, INITIAL_PERCENTAGE)
    window2 = gui.MainWindow(feather, communications, QApplication(sys.argv))
    window2.setup_ui()
    window2.start_ui()
    vehicle_moving = box(pos=vector(0,0,0),length=5,height=10,width=5)
    mover = Movement(initial_angle=vector(0,0,0), 
                     initial_position=vector(0,0,0), 
                     mcu=feather, 
                     initial_velocity=vector(0,0,0), 
                     vehicle=vehicle_moving)
    visualization = Visualizer(mover)


if __name__ == "__main__":
    start()
