import threading
from PyQt5 import QtGui
from PIL import ImageGrab
import numpy as np
import scipy.misc
import pygame
import cv2
import time
from database import Settings
import functions
import os
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_perspective_transform_matrix(img, bottom_width, top_width, height, offset, to_shape):
    shape = img.shape

    bottom_y = shape[0] - offset
    top_y = bottom_y - round(shape[0] * height)

    x_middle = round(shape[1]/2)
    bottom_x_half = round(shape[1] * bottom_width / 2)
    top_x_half = round(shape[1] * top_width / 2)

    src_points = np.float32([
        [x_middle - top_x_half, top_y],  # A - Top Left
        [x_middle + top_x_half, top_y],  # B - Top Right
        [x_middle + bottom_x_half, bottom_y],  # C - Bottom Right
        [x_middle - bottom_x_half, bottom_y],  # D - Bottom Left
    ])
    dst_points = np.float32([
        [0, 0],
        [to_shape[1], 0],
        to_shape,
        [0, to_shape[0]],
    ])

    return cv2.getPerspectiveTransform(src_points, dst_points), cv2.getPerspectiveTransform(dst_points, src_points)


def generate_column_histogram(image):
    """Returns a list where each value represents the amount of nonzero pixels."""
    histogram = list()
    for column_counter in range(image.shape[1]):
        column = image[:, column_counter]
        histogram.append(np.count_nonzero(column))
    return histogram


def get_content_of_sliding_window(image, abs_center, width, height, count=0):
    """Returns a width x height window where abs_center is the center."""
    y_bottom = image.shape[0] - height*count
    y_top = y_bottom - height

    if y_top < 0:
        return None

    x_left = abs_center - round(width/2)
    x_right = abs_center + round(width/2)
    window = image[y_top:y_bottom, x_left:x_right]

    return window


def get_centered_sliding_window(image, abs_center, width, height, count=0):
    """Returns a width x height window with corrected center and the value of the center in the whole image."""
    if not abs_center:
        return None, 0, 0

    window = get_content_of_sliding_window(image, abs_center, width, height, count)

    if not window.any():
        return None, 0, 0

    histogram = generate_column_histogram(window)
    # TODO: check if line is in the window
    window_center = histogram.index(max(histogram))
    # TODO: use mean instead of ma
    new_abs_center = abs_center - round(width/2) - window_center
    new_window = get_content_of_sliding_window(image, new_abs_center, width, height, count)
    return new_window, new_abs_center, max(histogram)


class AutopilotThread(threading.Thread):
    lock = threading.Lock()
    running = True

    def __init__(self, statusbar, controller_thread, image_front):
        threading.Thread.__init__(self, daemon=True)

        with AutopilotThread.lock:
            AutopilotThread.running = True

        pygame.init()
        pygame.joystick.init()

        self.statusbar = statusbar
        self.controller_thread = controller_thread
        self.image_front = image_front

        self.running = True
        self.country_code = Settings().get_value(Settings.COUNTRY_DEFAULT)
        self.b_autopilot = Settings().get_value(Settings.AUTOPILOT)
        self.steering_axis = Settings().get_value(Settings.STEERING_AXIS)
        self.joystick = pygame.joystick.Joystick(Settings().get_value(Settings.CONTROLLER))
        self.joystick.init()

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

        while AutopilotThread.running:
            pygame.event.pump()

            # Button to activate/deactivate autopilot
            autopilot_button_act = self.joystick.get_button(self.b_autopilot)
            # Button was pressed
            if autopilot_button_act != autopilot_button_prev and autopilot_button_act == 1:
                autopilot = not autopilot
                # if autopilot and settings.AUTOPILOT_SOUND_ACTIVATE:
                #    autopilot_engage.play()
            autopilot_button_prev = autopilot_button_act

            # Read the steering value of joystick
            axis = round((self.joystick.get_axis(self.steering_axis) + 1) * 32768 / 2)
            # Interrupt autopilot if manual steering was detected
            if abs(manual_steering_prev - axis) > 1000 and autopilot:
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

            ### Detect lane and steer ###
            # Do a perspective transformation of the lane.
            M, Minv = get_perspective_transform_matrix(main, 1, 0.2, 0.4, 0, [300, 300])
            image_warped = cv2.warpPerspective(main.copy(), M, (300, 300), flags=cv2.INTER_LINEAR)

            # Filter lane markings.
            lower_white = np.array([180, 180, 180])
            upper_white = np.array([255, 255, 255])
            mask = cv2.inRange(image_warped, lower_white, upper_white)
            image_warped_filtered = cv2.bitwise_and(image_warped, image_warped, mask=mask)
            _, image_warped_filtered_binary = cv2.threshold(image_warped_filtered, 1, 255, cv2.THRESH_BINARY)

            # # Find position of left and right markings.
            # histogram = generate_column_histogram(image_warped_filtered_binary)
            # left_markings = histogram.index(max(histogram[:150]))
            # right_markings = histogram.index(max(histogram[150:]))
            # log.debug((left_markings, right_markings))

            window_width = 75
            window_height = 50

            # First half (left markings)
            column_count = int(image_warped_filtered_binary.shape[1]/window_width)
            left_prediction = []
            right_prediction = []

            for column in range(0, int(column_count/2)):
                left_predicted_center = int(window_width/2 + column*window_width)
                left_prediction.append(get_centered_sliding_window(image_warped_filtered_binary,
                                                                   left_predicted_center,
                                                                   window_width, window_height))

                right_predicted_center = int(window_width / 2 + (column + column_count/2) * window_width)
                right_prediction.append(get_centered_sliding_window(image_warped_filtered_binary,
                                                                    right_predicted_center,
                                                                    window_width, window_height))

            # Select the sector with the highest maximum.
            left_markings_histogram_max = [x[2] for x in left_prediction]
            left_markings_center = [x[1] for x in left_prediction]
            left_markings = left_markings_center[left_markings_histogram_max.index(max(left_markings_histogram_max))]

            right_markings_histogram_max = [x[2] for x in right_prediction]
            right_markings_center = [x[1] for x in right_prediction]
            right_markings = right_markings_center[right_markings_histogram_max.index(max(right_markings_histogram_max))]

            log.debug(('LEFT', left_markings_center, left_markings_histogram_max))
            log.debug(('RIGHT', right_markings_center, right_markings_histogram_max))
            log.debug(('CHOSE', left_markings, right_markings))

            left_centers = [None]
            right_centers = [None]

            if left_markings > 0 and right_markings > 0:
                # Apply sliding window technique.
                window_count = int(image_warped_filtered_binary.shape[0]/window_height)

                left_centers = [left_markings]
                right_centers = [right_markings]

                # Go through all rows (from bottom to top of the image).
                for row in range(1, window_count):
                    if row > 0:
                        last_value = row-1
                    else:
                        last_value = 0

                    # Take the center (global position) of the last row and use it as entry point.
                    # Then look window_width/2 to the left and to the right and determine the more precise
                    # center in that area.
                    _, corrected_center_left, _ = get_centered_sliding_window(image_warped_filtered_binary,
                                                                              left_centers[last_value], window_width,
                                                                              window_height, row)
                    _, corrected_center_right, _ = get_centered_sliding_window(image_warped_filtered_binary,
                                                                               right_centers[last_value], window_width,
                                                                               window_height, row)
                    if row == 0:
                        left_centers = []
                        right_centers = []

                    left_centers.append(corrected_center_left)
                    right_centers.append(corrected_center_right)

                log.debug(('LEFT_CENTERS', left_centers))
                log.debug(('RIGHT_CENTERS', right_centers))

            lane_final_image = image_warped_filtered_binary.copy()
            if left_centers[0]:
                lane_final_image = cv2.line(lane_final_image, (left_centers[0], 0), (left_centers[0], 300), (255, 0, 0), 5)
            if right_centers[0]:
                lane_final_image = cv2.line(lane_final_image, (right_centers[0], 0), (right_centers[0], 300), (0, 255, 0), 5)

            # TODO: Determine center of lane and calculate degrees to reach this center.
            y_eval = 0
            degrees = y_eval * 180 / scipy.pi
            steering = int(round((degrees + 180) / 180 * 32768 / 2))  # Value for vjoy controller

            # Set the value of the vjoy joystick to the predicted steering angle
            if autopilot:
                self.controller_thread.set_angle(steering)
                self.statusbar.showMessage("Autopilot active")
            else:
                self.statusbar.showMessage("Autopilot inactive")

            # functions.set_image(main.copy(), self.image_front)
            functions.set_image(lane_final_image.copy(), self.image_front)
