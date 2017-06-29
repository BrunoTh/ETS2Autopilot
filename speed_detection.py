import cv2
import numpy as np
import os
import settings


### TRAINING ###
if os.path.exists("generalsamples.data"):
    path = ""
else:
    path = "../"
samples = np.loadtxt('%sgeneralsamples.data' % path, np.float32)
responses = np.loadtxt('%sgeneralresponses.data' % path, np.float32)
responses = responses.reshape((responses.size, 1))

model = cv2.ml.KNearest_create()
model.train(samples, cv2.ml.ROW_SAMPLE, responses)


def get_speed(frame):
    """
    :param frame: Captured image
    :return: Speed
    """
    speed = frame[settings.IMAGE_SPEED_Y[0]:settings.IMAGE_SPEED_Y[1], settings.IMAGE_SPEED_X[0]:settings.IMAGE_SPEED_X[1]]
    speed_gray = cv2.cvtColor(speed, cv2.COLOR_BGR2GRAY)

    # Zoom
    rows, cols = speed_gray.shape[:2]
    M = np.float32([[2, 0, 0], [0, 2, 0]])
    speed_zoom = cv2.warpAffine(speed_gray, M, (cols * 2, rows * 2))
    _, speed_threshold = cv2.threshold(speed_zoom, 210, 255, cv2.THRESH_BINARY)

    to_detect = speed_threshold[:, 26:]
    cv2.imshow('speed', to_detect)
    to_detect = cv2.resize(to_detect, (20, 20))
    to_detect = to_detect.reshape((1, 400))
    to_detect = np.float32(to_detect)
    _, results, _, _ = model.findNearest(to_detect, k=1)

    return int((results[0][0]))
