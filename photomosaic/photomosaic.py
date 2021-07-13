# photomosaic.py
# automatic system to do the photomosaic task.

import cv2
import numpy as np
import imutils

h3_to_h2 = 180 / 360
hue_ranges = {"purple": (250, 295),
              "yellow": (43, 70),
              "orange": (20, 42),
              "red": (0, 18),
              "red_2": (344, 359),
              "green": (75, 180),
              "blue": (181, 248),
              "pink": (300, 345),
              "brown": (22, 40)
              }
TARGET_WIDTH = 3360


def crop_rect(img, rect):
    # get the parameter of the small rectangle
    center = rect[0]
    size = rect[1]
    angle = rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))

    # get row and col num in img
    rows, cols = img.shape[0], img.shape[1]

    m = cv2.getRotationMatrix2D(center, angle, 1)
    img_rot = cv2.warpAffine(img, m, (cols, rows))
    out = cv2.getRectSubPix(img_rot, size, center)

    return out, img_rot


def get_cropped_image(path):
    # print(path)
    image = cv2.imread(path)
    im = image.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([64, 0, 0], dtype=np.uint8)
    upper_white = np.array([128, 100, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_white, upper_white)
    res = cv2.bitwise_and(image, image, mask=mask)
    grayscale = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
    thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    cnts = imutils.grab_contours(cnts)

    cv2.drawContours(thresh, cnts, -1, (0, 255, 0), 3)
    max_rect_size = 0
    cntr_rect = [[[0, 0], [0, 0], [0, 0], [0, 0]]]

    for i in cnts:
        epsilon = 0.05 * cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, epsilon, True)
        if len(approx) == 4:
            dims = (approx[3] - approx[1])[0]
            size = pow(dims[0] ** 2 + dims[1] ** 2, 0.5)
            if size > max_rect_size:
                cntr_rect[0] = approx
                cv2.drawContours(im, cntr_rect, -1, (0, 255, 0), 3)

    rect = cntr_rect[0]
    min_x = 10000
    min_y = 10000
    max_x = 0
    max_y = 0
    for val in rect:
        val = val[0]
        if val[0] < min_x:
            min_x = val[0]
        if val[1] < min_y:
            min_y = val[1]
        if val[0] > max_x:
            max_x = val[0]
        if val[1] > max_y:
            max_y = val[1]

    cropped = image[min_y:max_y, min_x:max_x]

    # find out if all colors in image: red, yellow, orange, brown, pink, purple, green, blue
    outs = {}
    positions = {"left": None, "right": None, "top": None, "bottom": None}
    pos_count = 0
    for key in hue_ranges:
        range = hue_ranges[key]
        hsv = cv2.cvtColor(cropped.copy(), cv2.COLOR_BGR2HSV)
        lower = np.array([range[0] * h3_to_h2, 75, 171 if key == "orange" else 0], dtype=np.uint8)
        upper = np.array([range[1] * h3_to_h2, 255, 171 if key == "brown" else 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        hue_image = cv2.bitwise_and(cropped, cropped, mask=mask)
        hue_gray = cv2.cvtColor(hue_image, cv2.COLOR_BGR2GRAY)
        hue_blur = cv2.GaussianBlur(hue_gray, (5, 5), 0)
        hue_thresh = cv2.threshold(hue_blur, 35, 255, cv2.THRESH_BINARY)[1]

        contours, hier = cv2.findContours(hue_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros(hue_thresh.shape, np.uint8)
        for cnt in contours:
            if 4000 < cv2.contourArea(cnt):
                # cv2.drawContours(cropped, [cnt], 0, (0, 0, 255), 2)
                cv2.drawContours(mask, [cnt], 0, 255, -1)
                moment = cv2.moments(cnt)
                center = (moment["m10"] / moment["m00"], moment["m01"] / moment["m00"])
                # get position
                width = cropped.shape[1]
                height = cropped.shape[0]
                k = key if key != "red_2" else "red"
                if width * 0.25 < center[0] < width * 0.75 and center[1] < height * 0.33:
                    positions["top"] = k
                if width * 0.25 < center[0] < width * 0.75 and center[1] > height * 0.67:
                    positions["bottom"] = k
                if width * 0.75 < center[0] and height * 0.33 < center[1] < height * 0.67:
                    positions["right"] = k
                if width * 0.25 > center[0] and height * 0.33 < center[1] < height * 0.67:
                    positions["left"] = k
                pos_count += 1
        if key == "red_2":
            outs["red"] = outs["red"] or np.sum(mask) > 1000000
        else:
            outs[key] = np.sum(mask) > 1000000
    return [cropped, outs, positions, pos_count]


def rotation_times(pos, search, to):
    rot = ['left', 'top', 'right', 'bottom']
    loc = None
    for key in pos:
        if pos[key] == search:
            loc = key
    if not loc:
        return 0
    return (rot.index(to) - rot.index(loc)) % 4


def stitch_images(path):
    rot = ['left', 'top', 'right', 'bottom']
    base_image = None
    other_side_images = []
    top_image = None
    for j in range(5):
        i = get_cropped_image(path + f"J{j + 1}.png")
        if i[3] == 4:
            top_image = i
        elif not base_image and i[0].shape[1] > 600:
            base_image = i
        else:
            other_side_images.append(i)

    # align base image
    base_rot_times = rotation_times(base_image[2], None, 'bottom')
    print("rotating base image", base_rot_times, "times")
    for k in range(base_rot_times):
        base_image[0] = cv2.rotate(base_image[0], cv2.cv2.ROTATE_90_CLOCKWISE)

    for r in range(base_rot_times):
        hold = base_image[2]['bottom']
        for key in rot:
            temp = base_image[2][key]
            base_image[2][key] = hold
            hold = temp

    # get left, right, back images
    left_image = None
    right_image = None
    back_image = None
    for image in other_side_images:
        if base_image[2]['left'] in image[2].values():
            left_image = image
        elif base_image[2]['right'] in image[2].values():
            right_image = image
        else:
            back_image = image

    # align top image
    top_rot_times = rotation_times(top_image[2], base_image[2]['top'], 'bottom')
    print("rotating top image", top_rot_times, "times")
    for k in range(top_rot_times):
        top_image[0] = cv2.rotate(top_image[0], cv2.cv2.ROTATE_90_CLOCKWISE)

    # align left image
    left_rot_times = rotation_times(left_image[2], base_image[2]['left'], 'right')
    print("rotating left image", left_rot_times, "times")
    for k in range(left_rot_times):
        left_image[0] = cv2.rotate(left_image[0], cv2.cv2.ROTATE_90_CLOCKWISE)

    # align right image
    right_rot_times = rotation_times(right_image[2], base_image[2]['right'], 'left')
    print("rotating right image", right_rot_times, "times")
    for k in range(right_rot_times):
        right_image[0] = cv2.rotate(right_image[0], cv2.cv2.ROTATE_90_CLOCKWISE)

    # get top color for back image
    # print("start: ", top_image[2])
    for r in range(top_rot_times):
        hold = top_image[2]['bottom']
        for key in rot:
            temp = top_image[2][key]
            top_image[2][key] = hold
            hold = temp
    back_image_top_color = top_image[2]['top']
    # print("end: ", top_image[2])

    # align back image
    back_rot_times = rotation_times(back_image[2], back_image_top_color, 'top')
    print("rotating back image", back_rot_times, "times")
    for k in range(back_rot_times):
        back_image[0] = cv2.rotate(back_image[0], cv2.cv2.ROTATE_90_CLOCKWISE)

    # get max height for bottom row
    max_height = 0
    for image in [left_image[0], base_image[0], right_image[0], back_image[0]]:
        if image.shape[0] > max_height:
            max_height = image.shape[0]
    left_image[0] = cv2.copyMakeBorder(left_image[0], max_height - left_image[0].shape[0], 0, 0, 0, cv2.BORDER_CONSTANT)
    right_image[0] = cv2.copyMakeBorder(right_image[0], max_height - right_image[0].shape[0], 0, 0, 0,
                                        cv2.BORDER_CONSTANT)
    back_image[0] = cv2.copyMakeBorder(back_image[0], max_height - back_image[0].shape[0], 0, 0, 0, cv2.BORDER_CONSTANT)
    base_image[0] = cv2.copyMakeBorder(base_image[0], max_height - base_image[0].shape[0], 0, 0, 0, cv2.BORDER_CONSTANT)

    # make top and base widths the same
    top_larger = top_image[0].shape[1] > base_image[0].shape[1]
    larger_width = top_image[0].shape[1] if top_image[0].shape[1] > base_image[0].shape[1] else base_image[0].shape[1]
    if top_larger:
        base_image[0] = cv2.copyMakeBorder(base_image[0], 0, 0, int((larger_width - base_image[0].shape[1]) / 2),
                                           int((larger_width - base_image[0].shape[1]) / 2 + 0.5),
                                           cv2.BORDER_CONSTANT)
    else:
        top_image[0] = cv2.copyMakeBorder(top_image[0], 0, 0, int((larger_width - top_image[0].shape[1]) / 2),
                                          int((larger_width - top_image[0].shape[1]) / 2 + 0.5), cv2.BORDER_CONSTANT)

    # concatenate images
    bottom_row = cv2.hconcat([left_image[0], base_image[0], right_image[0], back_image[0]])
    lshape = (top_image[0].shape[0], left_image[0].shape[1], 3)
    rshape = (top_image[0].shape[0], right_image[0].shape[1], 3)
    bshape = (top_image[0].shape[0], back_image[0].shape[1], 3)
    h = [np.zeros(lshape, dtype=np.uint8), top_image[0], np.zeros(rshape, dtype=np.uint8),
         np.zeros(bshape, dtype=np.uint8)]
    top_row = cv2.hconcat(h)
    photomosaic = cv2.vconcat([top_row, bottom_row])
    scale_factor = TARGET_WIDTH / photomosaic.shape[1]
    photomosaic = cv2.resize(photomosaic, (int(photomosaic.shape[1] * scale_factor),
                                           int(photomosaic.shape[0] * scale_factor)), interpolation=cv2.INTER_LINEAR)

    cv2.imshow("Subway Car Photomosaic", photomosaic)
    while True:
        if cv2.waitKey(33) == 32:
            break


class Photomosaic:
    def __init__(self, path):
        self.path = path

    def run(self):
        stitch_images(self.path)


if __name__ == "__main__":
    PATH = "C:/Users/xhex8/Documents/GitHub/mate-rnd-oqbot/photomosaic/data/"
    stitch_images(PATH)
