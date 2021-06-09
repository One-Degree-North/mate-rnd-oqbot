# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: str, shift: bool, ctrl: bool):
    	self.key = key
		self.shift = shift
		self.ctrl = ctrl
