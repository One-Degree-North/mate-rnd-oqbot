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
	self.HEIGHT_THRESH: int = 1				# CHANGE THIS
	self.ORIENTATION_THRESH: int = 5		# CHANGE THIS
	self.DISTANCE: int = 6					# CHANGE THIS
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
		
	def move(self, time_needed: float, trigger: str):
		pressed: bool = True
		self.comms.read_send(KeySignal(trigger, pressed))
		time.sleep(time_needed)
		pressed = False
		self.comms.read_send(KeySignal(trigger, pressed))
	
	# Can take CV approach too
	def adjust_orientation(self):
		left_trigger: str = "a"
		right_trigger: str = "d"
		starttime = time.time()
			
		while self.running:
			time_now = time.time()
			time_diff: float = time_now - start_time
			start_time = time_now
			
			TURN_INDEX: int = 0
			angvel: float = self.mcu.latest_orientation[TURN_INDEX]
			self.orientation = self.orientation + angvel * time_diff
			
			if abs(self.orientation) > self.ORIENTATION_THRESH:
				time_needed: float = abs(self.orientation) / angvel
					
				if self.orientation > 0:
					self.move(time_needed, left_trigger)
				elif self.orientation < 0:
					self.move(time_needed, right_trigger)
					
	def adjust_height(self):
		up_trigger: str = "e"				# CHANGE THIS
		down_trigger: str = "q"				# CHANGE THIS
		start_time = time.time()
		self.height: float = 0
			
		while self.running:
			time-now = time.time()
			time_diff: float = time_now - start_time
			starttime = timenow
			
			DOWN_AXIS_INDEX: int = 1		# CHANGE THIS
			accel: float = self.mcu.latest_accel[DOWN_AXIS_INDEX]
			self.height = self.height + 0.5 * self.accel * (time_diff ** 2)
			
			if abs(self.height) > self.HEIGHT_THRESH:
				time_needed: float = (2 * abs(self.height / accel)) ** 0.5
				
				if self.height > 0:			# Positive height, positive acceleration = higher, going up
					self.move(time_needed, down_trigger)
				elif self.height < 0:		# Negative height, negative acceleration = deeper, going down
					self.move(time_needed, up_trigger)
				
  	def navigate(self):
		self.forward_thread = threading.Thread(target = self.move_forward)
		self.forward_thread.start()
		self.adjust_orientation_thread = threading.Thread(target = self.adjust_orientation)
		self.adjust_orientation_thread.start()
		self.adjust_height_thread = threading.Thread(target = self.adjust_height)
		self.adjust_height_thread.start()
