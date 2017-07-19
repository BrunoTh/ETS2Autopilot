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

import scipy.misc
import random
import os
from database import Settings, Data

"""
sequence.txt information:
    - 0: filename of image
    - 1: steering angle
    - 2: speed
    - 3: acceleration (-100 = 100% throttle, 100 = 100% brake)
    - 4: indicator (0: none, 1: left, 2: right)
"""


class DrivingData(object):
    def __init__(self):
        self.settings = Settings()
        self.data = Data()

        country_string = self.settings.get_value(Settings.COUNTRIES_MODEL)
        countries = country_string.split(",")

        self.xs = []
        self.ys = []

        # points to the end of the last batch
        train_batch_pointer = 0
        val_batch_pointer = 0

        # Get all images
        self.image_list = []

        for country in countries:
            self.image_list += self.data.get_image_list_filter(country=country, maneuver=0)

        for image in self.image_list:
            self.steering_deg = float(image[2]) * scipy.pi / 180
            # higher steering angles are rare, so add four times
            # if abs(steering_deg) > 40:
            #    for i in range(int(steering_deg/10-2)*4):
            #        xs.append("../captured/" + line.split()[0])
            #        ys.append(steering_deg)

            self.xs.append(os.path.join("captured/", image[1]))
            # the paper by Nvidia uses the inverse of the turning radius,
            # but steering wheel angle is proportional to the inverse of turning radius
            # so the steering wheel angle in radians is used as the output
            self.ys.append(self.steering_deg)

        # get number of images
        self.num_images = len(self.xs)

        # shuffle list of images
        self.c = list(zip(self.xs, self.ys))
        random.shuffle(self.c)
        self.xs, self.ys = zip(*self.c)

        # Training data
        self.train_xs = self.xs[:int(len(self.xs) * 0.8)]
        self.train_ys = self.ys[:int(len(self.xs) * 0.8)]

        # Validation data
        self.val_xs = self.xs[-int(len(self.xs) * 0.2):]
        self.val_ys = self.ys[-int(len(self.xs) * 0.2):]

        self.num_train_images = len(self.train_xs)
        self.num_val_images = len(self.val_xs)

        print("Total data:", len(self.xs), self.num_images)
        print("Training data:", len(self.train_xs))
        print("Validation data:", len(self.val_xs))

    def LoadTrainBatch(self, batch_size):
        x_out = []
        y_out = []
        for i in range(0, batch_size):
            x_out.append(scipy.misc.imresize(scipy.misc.imread(self.train_xs[(self.train_batch_pointer + i) % self.num_train_images])[-150:], [66, 200]) / 255.0)
            y_out.append([self.train_ys[(self.train_batch_pointer + i) % self.num_train_images]])
        self.train_batch_pointer += batch_size
        return x_out, y_out


    def LoadValBatch(self, batch_size):
        x_out = []
        y_out = []
        for i in range(0, batch_size):
            x_out.append(scipy.misc.imresize(scipy.misc.imread(self.val_xs[(self.val_batch_pointer + i) % self.num_val_images])[-150:], [66, 200]) / 255.0)
            y_out.append([self.val_ys[(self.val_batch_pointer + i) % self.num_val_images]])
        self.val_batch_pointer += batch_size
        return x_out, y_out
