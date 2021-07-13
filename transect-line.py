import cv2

class TransectLine:
	def __init__(self, camera_id: int, blue_lower: (int, int, int), blue_upper: (int, int, int)):
		self.camera = cv2.VideoCapture(camera_id)
		self.BLUE_LOWER: (int, int, int) = blue_lower		# INPUT BLUE IN HSV
		self.BlUE_UPPER: (int, int, int) = blue_upper
		self.WIDTH = camera.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
		self.HEIGHT = camera.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
		self.RATIO_UPPER_BOUND = 0.8
		self.RATIO_LOWER_BOUND = 0.6
		
		if self.camera.isOpened():
			print("Footage opened!")
		
	def move_up(self):
		# Do something
		
	def move_down(self):
		# Do something
		
	def run(self):
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
			
			x1: int, _, w1: int, _ = cv2.boundingRect(contour_one)
			x2: int, _, w2: int, _ = cv2.boundingRect(contour_two)
			
			centre_c1 = x1 + w1/2
			centre_c2 = x2 + w2/2
			
			ratio = abs(centre_c1 - centre_c2) / self.WIDTH
			
			if ratio >= self.RATIO_UPPER_BOUND:
				self.move_up()
			
			if ratio <= self.RATIO_LOWER_BOUND:
				self.move_down()
