# Class that stores each key press as an object

class KeySignal:
	def __init__(self, key: str, pressed: bool):
		self.key: str = key
		self.pressed: bool = pressed
		key_ascii: int = ord(self.key)
		
		if key_ascii ^ 32 > key_ascii or key_ascii ^ 32 == 0:
			# key_ascii ^ 32 == 0 checks whether it is a space or not
			# Capital and small letters in binary are distinguished by the 32-bit digit
			# For example, A is 01000001 and a is 01100001
			# Performing an XOR operation is one of the fastest ways to switch the case of a letter
			self.shift = False
		else:
			self.shift = True
