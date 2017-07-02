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
from settings import COUNTRY

"""
sequence.txt information:
    - 0: filename of image
    - 1: steering angle
    - 2: speed
    - 3: acceleration (-100 = 100% throttle, 100 = 100% brake)
    - 4: indicator (0: none, 1: left, 2: right)
"""

xs = []
ys = []

# points to the end of the last batch
train_batch_pointer = 0
val_batch_pointer = 0

sequences = []
# read sequence.txt
with open("captured/sequence.txt") as f:
    for line in f:
        split = line.split()
        sequences.append([int(split[0]), int(split[1]), split[2], int(split[3])])


def get_country(img_id):
    """
    Every time you start recording images of you driving manually, a new sequence is created.
    I assume that every image in the sequence was recorded under the same conditions (like weather, road type or country).
    This function returns the country of the given image (id).
    """
    for i in range(len(sequences)-1):
        if img_id in range(sequences[i][0], sequences[i][1]):
            return sequences[i][2]

# read data.txt
with open("captured/data.txt") as f:
    for line in f:
        split = line.split()
        # Skip if indicator was active
        if len(split) == 5 and int(split[4]) != 0:
            continue
        # Skip if image was captured in country that we don't want in our actual model
        if get_country(int(split[0].split(".png")[0])) not in COUNTRY:
            continue

        steering_deg = float(line.split()[1]) * scipy.pi / 180

        # higher steering angles are rare, so add four times
        # if abs(steering_deg) > 40:
        #    for i in range(int(steering_deg/10-2)*4):
        #        xs.append("../captured/" + line.split()[0])
        #        ys.append(steering_deg)

        xs.append(os.path.join("captured/", line.split()[0]))
        # the paper by Nvidia uses the inverse of the turning radius,
        # but steering wheel angle is proportional to the inverse of turning radius
        # so the steering wheel angle in radians is used as the output
        ys.append(steering_deg)

# get number of images
num_images = len(xs)

# shuffle list of images
c = list(zip(xs, ys))
random.shuffle(c)
xs, ys = zip(*c)

# Training data
train_xs = xs[:int(len(xs) * 0.8)]
train_ys = ys[:int(len(xs) * 0.8)]

# Validation data
val_xs = xs[-int(len(xs) * 0.2):]
val_ys = ys[-int(len(xs) * 0.2):]

num_train_images = len(train_xs)
num_val_images = len(val_xs)

print("Total data:", len(xs), num_images)
print("Training data:", len(train_xs))
print("Validation data:", len(val_xs))


def LoadTrainBatch(batch_size):
    global train_batch_pointer
    x_out = []
    y_out = []
    for i in range(0, batch_size):
        x_out.append(scipy.misc.imresize(scipy.misc.imread(train_xs[(train_batch_pointer + i) % num_train_images])[-150:], [66, 200]) / 255.0)
        y_out.append([train_ys[(train_batch_pointer + i) % num_train_images]])
    train_batch_pointer += batch_size
    return x_out, y_out


def LoadValBatch(batch_size):
    global val_batch_pointer
    x_out = []
    y_out = []
    for i in range(0, batch_size):
        x_out.append(scipy.misc.imresize(scipy.misc.imread(val_xs[(val_batch_pointer + i) % num_val_images])[-150:], [66, 200]) / 255.0)
        y_out.append([val_ys[(val_batch_pointer + i) % num_val_images]])
    val_batch_pointer += batch_size
    return x_out, y_out
