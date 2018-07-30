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


def generate_column_historgram(image):
    """Returns a list where each value represents the amount of nonzero pixels."""
    histogram = list()
    for column_counter in range(image.shape[1]):
        column = image[:, column_counter]
        histogram.append(np.count_nonzero(column))
    return histogram


def get_content_of_sliding_window(image, abs_center, width, height, count=0):
    """Returns a width x height window where abs_center is the center."""
    y_bottom = image.shape[0] + height*count
    y_top = y_bottom + height

    if y_top > image.shape[0]:
        return None

    x_left = abs_center - round(width/2)
    x_right = abs_center + round(width/2)
    window = image[y_top:y_bottom, x_left:x_right]

    return window


def get_centered_sliding_window(image, abs_center, width, height, count=0):
    """Returns a width x height window with corrected center."""
    window = get_content_of_sliding_window(image, abs_center, width, height, count)
    histogram = generate_column_historgram(window)
    window_center = histogram.index(max(histogram))
    new_abs_center = abs_center - round(width/2) - window_center
    new_window = get_content_of_sliding_window(image, new_abs_center, width, height, count)
    return new_window


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
            M, Minv = get_perspective_transform_matrix(main, 1, 0.2, 0.4, 0, [300, 300])
            image_warped = cv2.warpPerspective(main.copy(), M, (300, 300), flags=cv2.INTER_LINEAR)
            # image_transformed = cv2.warpPerspective(image_transformed.copy(), Minv, image_transformed.shape[:2][::-1],
            #                                        flags=cv2.INTER_LINEAR)

            lower_white = np.array([180, 180, 180])
            upper_white = np.array([255, 255, 255])
            mask = cv2.inRange(image_warped, lower_white, upper_white)
            image_warped_filtered = cv2.bitwise_and(image_warped, image_warped, mask=mask)
            _, image_warped_filtered_binary = cv2.threshold(image_warped_filtered, 127, 255, cv2.THRESH_BINARY)

            histogram = generate_column_historgram(image_warped_filtered_binary)
            print(histogram.index(max(histogram[:150])), histogram.index(max(histogram[150:])))

            lane_final_image = image_warped_filtered_binary.copy()

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
            functions.set_image(lane_final_image.copy(), self.image_front)
