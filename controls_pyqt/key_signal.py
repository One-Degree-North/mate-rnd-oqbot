# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: str, pressed: bool):
		self.key: str = key
		self.pressed: bool = pressed
		
		if self.key ^ 32 > self.key or self.key ^ 32 == 0: # self.key ^ 32 == 0 checks whether it is a space or not
			self.shift = False
		else:
			self.shift = True
