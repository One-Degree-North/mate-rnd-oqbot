# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: str, pressed: bool):
		self.key: str = key
		self.pressed: bool = pressed
		
		if self.key ^ 32 > self.key or self.key ^ 32 == 0: # self.key^32 == 0 is checking whether it is a space
			self.shift = False
		elif self.key ^ 32 < self.key:
			self.shift = True
