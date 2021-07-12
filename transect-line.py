import cv2

class TransectLine:
	def __init__(self, camera_id: int, blue_lower: (int, int, int), blue_upper: (int, int, int)):
		self.camera = cv2.VideoCapture(camera_id)
		self.BLUE_LOWER: (int, int, int) = blue_lower		# INPUT BLUE IN HSV
		self.BlUE_UPPER: (int, int, int) = blue_upper
		
		if self.camera.isOpened():
			print("Footage opened!")
		
	def run():
		running = True
		while running: 
			_, frame = camera.read()
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			frame = cv2.GaussianBlur(frame, (15,15), 0)
			
			mask = cv2.inRange(frame, self.BLUE_LOWER, self.BLUE_UPPER)
			mask = cv2.erode(mask, None, iterations=2)
			mask = cv2.dilate(mask, None, iterations=2)
			
			contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			contours = sorted(contours, key=cv2.contourArea, reverse=True)
			
			contour_one = contours[0]
			contour_two = contours[1]
			
			# Find the distance between them
