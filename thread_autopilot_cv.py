import threading
from PyQt5 import QtGui
from PIL import ImageGrab
import tensorflow as tf
import numpy as np
import scipy.misc
import pygame
import cv2
import time
from database import Settings, Data
# import model
import functions
import os


# BEGIN USING CODE FROM Naoki Shibuya (https://github.com/naokishibuya/car-finding-lane-lines)
def average_slope_intercept(lines):
    left_lines = []  # (slope, intercept)
    left_weights = []  # (length,)
    right_lines = []  # (slope, intercept)
    right_weights = []  # (length,)

    for line in lines:
        for x1, y1, x2, y2 in line:
            if x2 == x1:
                continue  # ignore a vertical line
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            length = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
            if slope < 0:  # y is reversed in image
                left_lines.append((slope, intercept))
                left_weights.append((length))
            else:
                right_lines.append((slope, intercept))
                right_weights.append((length))

    # add more weight to longer lines
    left_lane = np.dot(left_weights, left_lines) / np.sum(left_weights) if len(left_weights) > 0 else None
    right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None

    return left_lane, right_lane  # (slope, intercept), (slope, intercept)


def make_line_points(y1, y2, line):
    """
    Convert a line represented in slope and intercept into pixel points
    """
    if line is None:
        return None

    slope, intercept = line

    # make sure everything is integer as cv2.line requires it
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    y1 = int(y1)
    y2 = int(y2)

    return ((x1, y1), (x2, y2))


def lane_lines(image, lines):
    left_lane, right_lane = average_slope_intercept(lines)

    y1 = image.shape[0]  # bottom of the image
    y2 = y1 * 0.6  # slightly lower than the middle

    left_line = make_line_points(y1, y2, left_lane)
    right_line = make_line_points(y1, y2, right_lane)

    return left_line, right_line


def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=20):
    # make a separate image to draw lines and combine with the orignal later
    line_image = np.zeros_like(image)
    for line in lines:
        if line is not None:
            cv2.line(line_image, *line, color, thickness)
    # image1 * α + image2 * β + λ
    # image1 and image2 must be the same shape.
    return cv2.addWeighted(image, 1.0, line_image, 0.95, 0.0)
# END USING CODE FROM Naoki Shibuya (https://github.com/naokishibuya/car-finding-lane-lines)


class AutopilotThread(threading.Thread):
    lock = threading.Lock()
    running = True

    def __init__(self, statusbar, controller_thread, steering_wheel, image_front):
        threading.Thread.__init__(self, daemon=True)

        with AutopilotThread.lock:
            AutopilotThread.running = True

        pygame.init()
        pygame.joystick.init()

        self.statusbar = statusbar
        self.controller_thread = controller_thread
        self.steering_wheel = steering_wheel
        self.image_front = image_front

        self.running = True
        self.country_code = Settings().get_value(Settings.COUNTRY_DEFAULT)
        self.b_autopilot = Settings().get_value(Settings.AUTOPILOT)
        self.steering_axis = Settings().get_value(Settings.STEERING_AXIS)
        self.joystick = pygame.joystick.Joystick(Settings().get_value(Settings.CONTROLLER))
        self.joystick.init()

        # self.sess = tf.InteractiveSession()
        # saver = tf.train.Saver()
        # saver.restore(self.sess, "save/model_%s.ckpt" % self.country_code)

    def stop(self):
        with AutopilotThread.lock:
            AutopilotThread.running = False

    def run(self):
        # Settings instance
        s = Settings()
        # State of autopilot
        autopilot = False
        # Previous state of the autopilot button
        autopilot_button_prev = 0
        # Previous value of steering (gamepad)
        manual_steering_prev = 0

        img_wheel = cv2.imread('steering_wheel_image.jpg', 0)
        rows, cols = img_wheel.shape

        while AutopilotThread.running:
            pygame.event.pump()

            # Button to activate/deactivate autopilot
            autopilot_button_act = self.joystick.get_button(self.b_autopilot)
            # Button was pressed
            if autopilot_button_act != autopilot_button_prev and autopilot_button_act == 1:
                autopilot = not autopilot
                #if autopilot and settings.AUTOPILOT_SOUND_ACTIVATE:
                #    autopilot_engage.play()
            autopilot_button_prev = autopilot_button_act

            # Read the steering value of joystick
            axis = round((self.joystick.get_axis(self.steering_axis) + 1) * 32768 / 2)
            # Interrupt autopilot if manual steering was detected
            if abs(manual_steering_prev - axis) > 1000 and autopilot:
                img_id = Data().get_next_fileid()
                sequence_id = Data().add_sequence(country=Settings().get_value(Settings.COUNTRY_DEFAULT), note="correction")
                self.controller_thread.set_autopilot(False)

                autopilot = False
            manual_steering_prev = axis

            self.controller_thread.set_autopilot(autopilot)

            # Get frame of game
            frame_raw = ImageGrab.grab(bbox=functions.get_screen_bbox())
            frame = np.uint8(frame_raw)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Relevant image region for steering angle prediction
            main = frame[s.get_value(Settings.IMAGE_FRONT_BORDER_TOP):s.get_value(Settings.IMAGE_FRONT_BORDER_BOTTOM),
                         s.get_value(Settings.IMAGE_FRONT_BORDER_LEFT):s.get_value(Settings.IMAGE_FRONT_BORDER_RIGHT)]
            # Resize the image to the size of the neural network input layer
            image = scipy.misc.imresize(main, [66, 200]) / 255.0

            # Detect lane and steer
            # BEGIN USING CODE FROM Naoki Shibuya (https://github.com/naokishibuya/car-finding-lane-lines)
            lane_hls = cv2.cvtColor(main, cv2.COLOR_RGB2HLS)
            # lane_hls = main.copy()
            # White color mask
            lower = np.uint8([0, 200, 0])
            upper = np.uint8([255, 255, 255])
            lane_white_mask = cv2.inRange(lane_hls, lower, upper)
            lane_white = cv2.bitwise_and(main, main, mask=lane_white_mask)

            lane_gray = cv2.cvtColor(lane_white, cv2.COLOR_RGB2GRAY)
            lane_gauss = cv2.GaussianBlur(lane_gray, (15, 15), 0)
            lane_canny = cv2.Canny(lane_gauss, 50, 150)
            # TODO: find region of interest
            lane_roi = lane_canny
            lane_hough_lines = cv2.HoughLinesP(lane_roi, rho=1, theta=np.pi/180, threshold=20, minLineLength=20,
                                               maxLineGap=300)
            if lane_hough_lines is not None and len(lane_hough_lines) > 0:
                lane_final_image = draw_lane_lines(main, lane_lines(main, lane_hough_lines))
            else:
                lane_final_image = main.copy()
            # END USING CODE FROM Naoki Shibuya

            # TODO: Determine center of lane and calculate degrees to reach this center.
            # y_eval = model.y.eval(session=self.sess, feed_dict={model.x: [image], model.keep_prob: 1.0})[0][0]
            y_eval = 0
            degrees = y_eval * 180 / scipy.pi
            steering = int(round((degrees + 180) / 180 * 32768 / 2))  # Value for vjoy controller

            # Set the value of the vjoy joystick to the predicted steering angle
            if autopilot:
                self.controller_thread.set_angle(steering)
                self.statusbar.showMessage("Autopilot active")
            else:
                self.statusbar.showMessage("Autopilot inactive")

            # TODO: Show steering wheel in GUI
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), -degrees, 1)
            dst = cv2.warpAffine(img_wheel, M, (cols, rows))
            # functions.set_image(dst.copy(), self.steering_wheel)

            # functions.set_image(main.copy(), self.image_front)
            cv2.imshow('canny', lane_canny)
            functions.set_image(lane_final_image.copy(), self.image_front)
