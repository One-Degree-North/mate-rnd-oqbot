import threading
import time

from mcu_lib.mcu import MCUInterface
from mcu_lib.command_constants import *
from comms import Communications
from controls_pyqt.key_signal import KeySignal


class TransectLine:
	def __init__(self, comms: Communications, mcu_object: MCUInterface):
    	self.comms: Communications = comms
    	self.mcu: MCUInterface = mcu_object
		self.HEIGHT_THRESH: int = 1			# CHANGE THIS
		self.INITIAL_ORIENTATION: int[] = self.mcu.latest_orienation
		self.DISTANCE: int = 6				# CHANGE THIS
		self.running = True
			
	def move_forward(self):
		trigger: str = "w"
		pressed: bool = True
		starttime = time.time()
		self.comms.read_send(KeySignal(trigger, pressed))
		self.distance_travelled: float = 0
		
		while(self.distance_travelled < self.DISTANCE):
			timenow = time.time()
			time_diff: float = timenow - starttime
			starttime = timenow
			
			FORWARD_AXIS_INDEX: int = 0		# CHANGE THIS
			accel: float = self.mcu.latest_accel[FORWARD_AXIS_INDEX]
			
			self.distance_travelled = self.distance_travelled + 0.5 * accel * (time_diff ** 2)
		
		pressed = False
		self.comms.read_send(KeySignal(trigger, pressed))
		self.running = False
		
	def adjust_orientation(self):
		while self.running:
			### DO SOMETHING
		
	def adjust_height(self):
		up_trigger: str = "e"				# CHANGE THIS
		down_trigger: str = "q"				# CHANGE THIS
		starttime = time.time()
		self.height: float = 0
			
		while self.running:
			timenow = time.time()
			time_diff: float = timenow - starttime
			starttime = timenow
			
			DOWN_AXIS_INDEX: int = 1		# CHANGE THIS
			accel: float = self.mcu.latest_accel[DOWN_AXIS_INDEX]
			self.height = self.height + 0.5 * self.accel * (time_diff ** 2)
			
			if abs(self.height) > self.HEIGHT_THRESH:
				timeneeded: float = (2 * abs(self.height / accel)) ** 0.5
				
				if self.height > 0:			# Positive height, positive acceleration = higher, going up
					pressed: bool = True
					self.comms.read_send(KeySignal(down_trigger, pressed))
					time.sleep(timeneeded)
					pressed = False
					self.comms.read_send(KeySignal(down_trigger, pressed))
				elif self.height < 0:		# Negative height, negative acceleration = deeper, going down
					pressed: bool = True
					self.comms.read_send(KeySignal(up_trigger, pressed))
					time.sleep(timeneeded)
					pressed = False
					self.comms.read_send(KeySignal(up_trigger, pressed))
				
  	def navigate(self):
    	#x_orientation: int = self.mcu.latest_orientation[0]
    	#y_orientation: int = self.mcu.latest_orientation[1]
		#z_orientation: int = self.mcu.latest_orientation[2]
			
		self.forward_thread = threading.Thread(target = self.move_forward)
		self.forward_thread.start()
		self.adjust_orientation_thread = threading.Thread(target = self.adjust_orientation)
		self.adjust_orientation_thread.start()
		self.adjust_height_thread = threading.Thread(target = self.adjust_height)
		self.adjust_height_thread.start()
