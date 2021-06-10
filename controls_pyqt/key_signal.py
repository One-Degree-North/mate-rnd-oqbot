# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: str, pressed: bool):
		self.key: str = key
		self.pressed: bool = pressed
		
		if self.key.islower():
			self.shift = False
		else:
			self.shift = True
