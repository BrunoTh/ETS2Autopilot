from database import Data, Settings

"""
data.txt information:
    - 0: filename of image
    - 1: steering angle
    - 2: speed
    - 3: acceleration (-100 = 100% throttle, 100 = 100% brake)
    - 4: indicator (0: none, 1: left, 2: right)
"""


def get_sid(sequences, img_id):
    for sequence in sequences:
        if img_id in range(sequence[0], sequence[1]):
            return sequence[2]


def migrate():
    data = Data()

    sequences = []
    # read sequence.txt
    with open("captured/sequence.txt") as f:
        for line in f:
            split = line.split()
            # Start, End, Country, Type
            sid = data.add_sequence(split[2], int(split[3]))
            sequences.append([int(split[0]), int(split[1]), sid])

    # read data.txt
    with open("captured/data.txt") as f:
        for line in f:
            split = line.split()
            sid = get_sid(sequences, int(split[0].split(".png")[0]))
            data.add_image(split[0], split[1], split[2], split[3], split[4], sid)
