import cv2
import sys

RATIO_UPPER_BOUND = 0.8
RATIO_LOWER_BOUND = 0.6
TIME_TO_MOVE_UP_AND_DOWN = 1

BAUD_RATE: int = 230400
CLOSE_ON_STARTUP: bool = True
MAX_READ: int = 16

port_list = list_ports.comports()
if not port_list:
    print("No available tty/COM ports. Halting!")
    exit()
port_list = [x.device for x in port_list]
if len(port_list) == 1:
    PORT = port_list[0]
    print(f"Using port {PORT}")
else:
    print(f"List of available tty/COM ports: {port_list}")
    PORT = input("Port to use: ")
    if len(PORT) == 0:
        PORT = "/dev/ttyUSB0"

REFRESH_RATE: int = 1440

INITIAL_PERCENTAGE: int = 25
SENSITIVE_PERCENTAGE: int = 15
	
feather = mcu.MCUInterface(PORT,
			   baud=BAUD_RATE,
			   close_on_startup=CLOSE_ON_STARTUP,
			   refresh_rate=REFRESH_RATE,
			   max_read=MAX_READ)
communications = comms.Communications(feather, SENSITIVE_PERCENTAGE, INITIAL_PERCENTAGE)

def move_up():
	comms.up(SENSITIVE_PERCENTAGE)
	time.sleep(TIME_TO_MOVE_UP_AND_DOWN)
	comms.up(0)

def move_down():
	comms.down(SENSITIVE_PERCENTAGE)
	time.sleep(TIME_TO_MOVE_UP_AND_DOWN)
	comms.down(0)
	
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
		comms.forward(INITIAL_PERCENTAGE)
	else:
		print("Error: camera not found!"
		break

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
	communications.start_elec_ops()
	communications.start_thread()
	
	camera_id: int = 0
	blue_lower: (int, int, int) = (209, 61, 67)
	blue_upper: (int, int, int) = (241, 100, 100)
		
	run(camera_id, blue_lower, blue_upper)
	
	communications.kill_elec_ops()
	sys.exit()
	# Movement and HSV thresholds
