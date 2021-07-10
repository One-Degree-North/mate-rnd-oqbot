# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: int, key_str: str, pressed: bool):
		self.key: int = key
		self.key_str: str = key_str
		self.pressed: bool = pressed

		if self.key_str.islower():
			self.shift = False
		else:
			self.shift = True
