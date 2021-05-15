import logging
import math
import time
from PIL import Image
from naoqi import ALProxy
import cv2
import numpy as np

_SHOW_IMAGE = True
maskHeight = 0.2
lowerColourH = 0
lowerColourS = 0
lowerColourV = 205
upperColourH = 110
upperColourS = 66
upperColourV = 255
IP = '192.168.1.107'
PORT = 9559

moveConfig = [["MaxStepX", 0.025],
              ["MaxStepY", 0.011],
              ["MaxStepTheta", 0.075],
              ["MaxStepFrequency", 0.98],
              ["StepHeight", 0],
              ["TorsoWx", 0.0],
              ["TorsoWx", 0.0]]

class HandCodedLaneFollower(object):

    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        logging.info('Creating a HandCodedLaneFollower...')
        self.curr_steering_angle = 90

    def getAngle(self):
        return self.curr_steering_angle

    def follow_lane(self, frame):
        # Main entry point of the lane follower
        show_image("orig", frame)

        lane_lines, frame = detect_lane(frame)
        final_frame = self.steer(frame, lane_lines)

        return final_frame

    def steer(self, frame, lane_lines):
        logging.debug('steering...')
        if len(lane_lines) == 0:
            logging.error('No lane lines detected, nothing to do.')
            return frame

        new_steering_angle = compute_steering_angle(frame, lane_lines)
        self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle,
                                                            len(lane_lines))

        curr_heading_image = display_heading_line(frame, self.curr_steering_angle)

        show_image("heading", curr_heading_image)

        return curr_heading_image


############################
# Frame processing steps
############################
def detect_edges(frame):
    # filter for blue lane lines
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    show_image("hsv", frame)
    lower_colour = np.array([lowerColourH, lowerColourS, lowerColourV])
    upper_colour = np.array([upperColourH, upperColourS, upperColourV])
    mask = cv2.inRange(frame, lower_colour, upper_colour)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    show_image("blue mask", mask)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges


def detect_lane(frame):
    logging.debug('detecting lane lines...')

    edges = detect_edges(frame)
    show_image('edges', edges)

    cropped_edges = region_of_interest(edges)
    show_image('edges cropped', cropped_edges)

    line_segments = detect_line_segments(cropped_edges)
    line_segment_image = display_lines(frame, line_segments)
    show_image("line segments", line_segment_image)

    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)
    show_image("lane lines", lane_lines_image)

    return lane_lines, lane_lines_image


def region_of_interest(canny):
    height, width = canny.shape
    mask = np.zeros_like(canny)

    # only focus bottom half of the screen

    polygon = np.array([[
        (0, int(height * maskHeight)),
        (width, int(height * maskHeight)),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    show_image("mask", mask)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image


def detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=8,
                                    maxLineGap=4)

    if line_segments is not None:
        for line_segment in line_segments:
            logging.debug('detected line_segment:')
            logging.debug("%s of length %s" % (line_segment, length_of_line_segment(line_segment[0])))

    return line_segments


def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1 / 3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary  # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines


def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02  # 0.0 means car pointing to center, -0.03: car is centered to left,
        # +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by pi_car front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle


def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines,
                             max_angle_deviation_two_lines=10, max_angle_deviation_one_lane=5):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """
    if num_of_lane_lines == 2:
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else:
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane

    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
                                        + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))

    return stabilized_steering_angle


############################
# Utility Functions
############################
def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image


def length_of_line_segment(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)


def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * maskHeight)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


############################
# Test Functions
############################
def test_photo(photo_file):
    land_follower = HandCodedLaneFollower()
    frame = cv2.imread(photo_file)
    combo_image = land_follower.follow_lane(frame)
    show_image('final', combo_image, True)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_video(video_file):
    lane_follower = HandCodedLaneFollower()
    cap = cv2.VideoCapture(video_file)
    # cap = cv2.VideoCapture(0)

    fps = 30

    # skip first second of video.
    for i in range(3):
        _, frame = cap.read()

    # video_type = cv2.VideoWriter_fourcc(*'XVID')
    # video_overlay = cv2.VideoWriter("%s_overlay.avi" % video_file, video_type, 20.0, (320, 240))
    timeStart = 0
    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            # print('frame %s' % i)
            logging.info('frame %s' % i)
            combo_image = lane_follower.follow_lane(frame)

            # cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)

            # cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
            # video_overlay.write(combo_image)
            cv2.imshow("Road with Lane line", combo_image)

            i += 1
            timeEnd = int(time.perf_counter() * 1000)
            timeSleep = 1
            if timeEnd - timeStart < 1000 // fps:
                timeSleep = 1000 // fps - timeEnd + timeStart
            a = cv2.waitKey(timeSleep) & 0xFF
            if a == ord('q'):
                break
            if a == ord('a'):
                cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)
                cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
            timeStart = int(time.perf_counter() * 1000)
    finally:
        cap.release()
        # video_overlay.release()
        cv2.destroyAllWindows()


def test_video_nao(ip, port):
    camProxy = ALProxy("ALVideoDevice", ip, port)
    motionProxy = ALProxy("ALMotion", ip, port)
    camProxy.setActiveCamera(1)
    videoClient = camProxy.subscribe("python_client", 2, 11, 5)
    if (not motionProxy.robotIsWakeUp()):
        motionProxy.wakeUp()
    motionProxy.moveInit()
    i = 0
    lane_follower = HandCodedLaneFollower()
    fps = 20
    timeStart = 0
    while True:
        naoImage = camProxy.getImageRemote(videoClient)
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]

        im = Image.frombytes("RGB", (imageWidth, imageHeight), array)
        frame = np.array(im)
        # print('frame %s' % i)
        logging.info('frame %s' % i)
        combo_image = lane_follower.follow_lane(frame)

        # cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)

        # cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
        # video_overlay.write(combo_image)
        cv2.imshow("Road with Lane line", combo_image)

        i += 1
        # timeEnd = int(time.perf_counter() * 1000)
        # timeSleep = 1
        # if timeEnd - timeStart < 1000 // fps:
        #     timeSleep = 1000 // fps - timeEnd + timeStart
        # a = cv2.waitKey(timeSleep) & 0xFF
        angle = lane_follower.getAngle()
        motionProxy.move(.1, 0, (90 - angle) * np.pi / 180, moveConfig)
        print angle
        a = cv2.waitKey(100) & 0xFF
        if a == ord('q'):
            motionProxy.stopMove()
            break
        if a == ord('a'):
            cv2.imwrite("%s_%03d_%03d.png" % ("nao", i, lane_follower.curr_steering_angle), frame)
            cv2.imwrite("%s_overlay_%03d.png" % ("nao", i), combo_image)
        # timeStart = int(time.perf_counter() * 1000)
    camProxy.unsubscribe(videoClient)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)
    # test_video(0)
    test_video_nao(IP, PORT)
    # test_video(r"C:\Users\yan\Desktop\DeepPiCar\models\lane_navigation\data\images\video01.avi")
    # test_photo('/home/pi/DeepPiCar/driver/data/video/car_video_190427_110320_073.png')
    # test_photo(sys.argv[1])
    # test_video(sys.argv[1])
