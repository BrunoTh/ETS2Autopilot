"""
MIT License

Original: https://github.com/SullyChen/Autopilot-TensorFlow
Copyright (c) 2016 Sully Chen

Modification: https://github.com/BrunoTh/ETS2Autopilot
Copyright (c) 2017 Bruno Thienel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tensorflow as tf
import scipy.misc
import model
import cv2
from PIL import ImageGrab
import pygame
import pyvjoy
import numpy as np
from subprocess import call
from speed_detection import get_speed
import settings

# Load model
COUNTRY_CODE = settings.COUNTRY_CODE
sess = tf.InteractiveSession()
saver = tf.train.Saver()
saver.restore(sess, "save/model_%s.ckpt" % COUNTRY_CODE)

# State of autopilot
autopilot = False
# Previous state of the autopilot button
autopilot_button_prev = 0
# Previous value of steering (gamepad)
manual_steering_prev = 0

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()
pygame.joystick.init()
# Print all available devices
print([pygame.joystick.Joystick(x).get_name() for x in range(pygame.joystick.get_count())])
joystick = pygame.joystick.Joystick(settings.JOYSTICK)
joystick.init()

# Sound that is played when autopilot gets activated
if settings.AUTOPILOT_SOUND_ACTIVATE:
    autopilot_engage = pygame.mixer.Sound(settings.AUTOPILOT_SOUND_ACTIVATE)
    autopilot_engage.set_volume(0.4)

vjoy = pyvjoy.VJoyDevice(settings.VJOY_DEVICE)
vjoy.reset()

img = cv2.imread('steering_wheel_image.jpg', 0)
rows, cols = img.shape

while cv2.waitKey(1) != ord('q'):
    pygame.event.pump()

    # Button to activate/deactivate autopilot
    autopilot_button_act = joystick.get_button(settings.AUTOPILOT_BUTTON)
    # Button was pressed
    if autopilot_button_act != autopilot_button_prev and autopilot_button_act == 1:
        autopilot = not autopilot
        if autopilot and settings.AUTOPILOT_SOUND_ACTIVATE:
            autopilot_engage.play()
    autopilot_button_prev = autopilot_button_act

    # Read the steering value of joystick
    axis = round((joystick.get_axis(settings.STEERING_AXIS) + 1) * 32768 / 2)
    # Interrupt autopilot if manual steering was detected
    if abs(manual_steering_prev - axis) > 1000:
        autopilot = False
    manual_steering_prev = axis

    print(autopilot)

    # If autopilot is not active, pass steering value of joystick to vjoy device
    if not autopilot:
        print(axis, (axis/32768*2-1)*180)
        vjoy.set_axis(pyvjoy.HID_USAGE_Y, axis)

    # Get frame of game
    frame_raw = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    frame = cv2.cvtColor(np.array(frame_raw), cv2.COLOR_RGB2BGR)

    # Steering strength depends on speed.
    factor = 1
    if settings.ADAPTIVE_STEERING:
        if get_speed(frame) > 70:
            factor = 1.06

    # Relevant image region for steering angle prediction
    main = frame[settings.IMAGE_FRONT_Y[0]:settings.IMAGE_FRONT_Y[1], settings.IMAGE_FRONT_X[0]:settings.IMAGE_FRONT_X[1]]
    # Resize the image to the size of the neural network input layer
    image = scipy.misc.imresize(main, [66, 200]) / 255.0
    # Let the neural network predict the new steering angle
    y_eval = model.y.eval(feed_dict={model.x: [image], model.keep_prob: 1.0})[0][0]
    degrees = y_eval * 180 * factor / scipy.pi
    steering = int(round((degrees+180)/180 * 32768/2))  # Value for vjoy controller

    # Set the value of the vjoy joystick to the predicted steering angle
    if autopilot:
        print(steering)
        vjoy.set_axis(pyvjoy.HID_USAGE_Y, steering)

    call("clear")
    print("Predicted steering angle: " + str(degrees) + " degrees")
    # Show, what the neural network "sees"
    cv2.imshow('frame', main)
    M = cv2.getRotationMatrix2D((cols/2, rows/2), -degrees, 1)
    dst = cv2.warpAffine(img, M, (cols, rows))
    cv2.imshow("steering wheel", dst)

cv2.destroyAllWindows()
