import threading
import pygame
import numpy as np
from PIL import ImageGrab
import cv2
from database import Settings, Data
import speed_detection
import functions


class RecordingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.joystick = pygame.joystick.Joystick(Settings().get_value(Settings.CONTROLLER))

    def stop(self):
        self.running = False

    def run(self):
        s = Settings()
        d = Data()

        img_id = d.get_next_fileid()

        while(self.running):
            pygame.event.pump()
            recording_button_act = self.joystick.get_button(s.get_value(Settings.AUTOPILOT))
            if recording_button_act != recording_button_prev and recording_button_act == 1:
                recording = not recording

                if recording:  # started recording
                    sequence_id = d.add_sequence(country=s.get_value(Settings.COUNTRY_DEFAULT))

            recording_button_prev = recording_button_act

            indicator_left_act = self.joystick.get_button(s.get_value(Settings.LEFT_INDICATOR))
            if indicator_left_act != indicator_left_prev and indicator_left_act == 1:
                indicator_left = not indicator_left

                # Switch indicator
                if indicator_left and indicator_right:
                    indicator_right = False
            indicator_left_prev = indicator_left_act

            indicator_right_act = self.joystick.get_button(s.get_value(Settings.RIGHT_INDICATOR))
            if indicator_right_act != indicator_right_prev and indicator_right_act == 1:
                indicator_right = not indicator_right

                # Switch indicator
                if indicator_right and indicator_left:
                    indicator_left = False
            indicator_right_prev = indicator_right_act

            if indicator_left:
                maneuver = 1
            elif indicator_right:
                maneuver = 2
            else:
                maneuver = 0

            # Capture the whole game
            frame_raw = ImageGrab.grab(bbox=functions.get_screen_bbox())
            frame = cv2.cvtColor(np.array(frame_raw), cv2.COLOR_RGB2BGR)

            main = frame[s.get_value(Settings.IMAGE_FRONT_BORDER_TOP):s.get_value(Settings.IMAGE_FRONT_BORDER_BOTTOM),
                         s.get_value(Settings.IMAGE_FRONT_BORDER_LEFT): s.get_value(Settings.IMAGE_FRONT_BORDER_RIGHT)]
            # gray = cv2.cvtColor(main, cv2.COLOR_BGR2GRAY)
            # blur_gray = cv2.GaussianBlur(gray, (3, 3), 0)
            # edges = cv2.Canny(blur_gray, 50, 150)
            # dilated = cv2.dilate(edges, (3,3), iterations=2)

            # Resize image to save some space (height = 100px)
            ratio = main.shape[1] / main.shape[0]
            resized = cv2.resize(main, (round(ratio * 100), 100))

            # cv2.imshow('cap', dilated)
            cv2.imshow('resized', resized)

            axis = self.joystick.get_axis(s.get_value(Settings.STEERING_AXIS)) * 180  # -180 to 180 "degrees"
            throttle = self.joystick.get_axis(s.get_value(Settings.THROTTLE_AXIS)) * 100  # -100=full throttle, 100=full brake

            speed = speed_detection.get_speed(frame)

            # Save frame every 150ms
            if recording and (functions.current_milli_time() - last_record) >= 150:
                last_record = functions.current_milli_time()
                cv2.imwrite("captured/%d.png" % img_id, resized)
                d.add_image("%d.png" % img_id, axis, speed, throttle, maneuver, sequence_id)
                img_id += 1
