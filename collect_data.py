import pygame
import numpy as np
import cv2
from PIL import ImageGrab
import os
import time
import speed_detection
import settings


def get_last_id():
    if os.path.exists("captured/data.txt"):
        with open("captured/data.txt") as f:
            lines = f.readlines()
            if len(lines) > 0:
                return int(lines[-1].split()[0].split(".png")[0])+1
            else:
                return 0
    else:
        return 0


def current_milli_time():
    return int(round(time.time() * 1000))


if not os.path.exists("captured"):
    os.mkdir("captured")

img_id = get_last_id()
recording = False
recording_button_prev = 0

maneuver = 0  # 0 - normal, 1 - indicator left, 2 - indicator right
indicator_left = False
indicator_left_prev = 0
indicator_right = False
indicator_right_prev = 0

last_record = 0

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(settings.JOYSTICK)
joystick.init()

data_file = open("captured/data.txt", "a")
sequence_file = open("captured/sequence.txt", "a")
sequence_start = img_id
sequence_end = img_id
sequence_country = settings.COUNTRY_CODE
sequence_type = -1  # 0 - Autobahn, 1 - Land, 2 - City

while True:
    pygame.event.pump()
    recording_button_act = joystick.get_button(settings.AUTOPILOT_BUTTON)
    if recording_button_act != recording_button_prev and recording_button_act == 1:
        recording = not recording

        if recording:  # started recording
            sequence_start = img_id
        else:  # stopped recording
            sequence_end = img_id-1
            sequence_file.write("%d %d %s %d\n" % (sequence_start, sequence_end, sequence_country, sequence_type))
    recording_button_prev = recording_button_act

    indicator_left_act = joystick.get_button(settings.INDICATOR_LEFT_BUTTON)
    if indicator_left_act != indicator_left_prev and indicator_left_act == 1:
        indicator_left = not indicator_left

        # Switch indicator
        if indicator_left and indicator_right:
            indicator_right = False
    indicator_left_prev = indicator_left_act

    indicator_right_act = joystick.get_button(settings.INDICATOR_RIGHT_BUTTON)
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
    frame_raw = ImageGrab.grab(bbox=(settings.GAME_WINDOW_X[0], settings.GAME_WINDOW_Y[0], settings.GAME_WINDOW_X[1],
                                     settings.GAME_WINDOW_Y[1]))
    frame = cv2.cvtColor(np.array(frame_raw), cv2.COLOR_RGB2BGR)

    main = frame[settings.IMAGE_FRONT_Y[0]:settings.IMAGE_FRONT_Y[1], settings.IMAGE_FRONT_X[0]:settings.IMAGE_FRONT_X[1]]
    # gray = cv2.cvtColor(main, cv2.COLOR_BGR2GRAY)
    # blur_gray = cv2.GaussianBlur(gray, (3, 3), 0)
    # edges = cv2.Canny(blur_gray, 50, 150)
    # dilated = cv2.dilate(edges, (3,3), iterations=2)

    # Resize image to save some space (height = 100px)
    ratio = main.shape[1]/main.shape[0]
    resized = cv2.resize(main, (round(ratio*100), 100))

    # cv2.imshow('cap', dilated)
    cv2.imshow('resized', resized)

    axis = joystick.get_axis(settings.STEERING_AXIS)*180  # -180 to 180 "degrees"
    throttle = joystick.get_axis(settings.THROTTLE_AXIS) * 100  # -100=full throttle, 100=full brake

    speed = speed_detection.get_speed(frame)
    print(recording, axis, speed, throttle, sequence_start if recording else sequence_end, maneuver)

    # Save frame every 150ms
    if recording and (current_milli_time() - last_record) >= 150:
        last_record = current_milli_time()
        cv2.imwrite("captured/%d.png" % img_id, resized)
        data_file.write("%d.png %f %d %f %d\n" % (img_id, axis, speed, throttle, maneuver))
        img_id += 1

    # Press ESC to exit
    if cv2.waitKey(30) == 27:
        break

data_file.close()
print(img_id)
cv2.destroyAllWindows()
