import cv2

RATIO_UPPER_BOUND = 0.8
RATIO_LOWER_BOUND = 0.6

def move_up():
	# Do something

def move_down():
	# Do something
	
def ended(frame):
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	_ , gray_mask = cv2.threshold(frame_gray, 0, 50, cv2.THRESH_BINARY)
	gray_contours = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	if len(gray_contours) != 0:
		return True
	
	return False

def ratio_check(x1, w1, x2, w2):
	centre_c1 = x1 + w1/2
	centre_c2 = x2 + w2/2
	ratio = abs(centre_c1 - centre_c2) / WIDTH

	if ratio >= RATIO_UPPER_BOUND:
		move_up()

	if ratio <= RATIO_LOWER_BOUND:
		move_down()

def run(camera_id: int, blue_lower: (int, int, int), blue_upper: (int, int, int)):
	camera = cv2.VideoCapture(camera_id)
	WIDTH = camera.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
	HEIGHT = camera.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
	
	BLUE_LOWER: (int, int, int) = blue_lower		# INPUT BLUE IN HSV
	BlUE_UPPER: (int, int, int) = blue_upper
	
	if camera.isOpened():
		print("Footage opened!")

	# start moving
	running = True
	while running: 
		_, frame = camera.read()
		frame = cv2.GaussianBlur(frame, (15,15), 0)
		frame = frame[HEIGHT/2 : HEIGHT, :]

		if ended(frame):
			running = False
			break

		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(frame, BLUE_LOWER, BLUE_UPPER)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key=cv2.contourArea, reverse=True)

		contour_one = contours[0]
		contour_two = contours[1]
		x1: int, _, w1: int, _ = cv2.boundingRect(contour_one)
		x2: int, _, w2: int, _ = cv2.boundingRect(contour_two)

		ratio_check(x1, w1, x2, w2)

	# stop moving

if __name__ == "__main__":
	camera_id: int = 0
	blue_lower: (int, int, int) = ( , , )
	blue_upper: (int, int, int) = ( , , )
	run(camera_id, blue_lower, blue_upper)
