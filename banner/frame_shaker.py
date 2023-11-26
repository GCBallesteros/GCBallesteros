from collections import namedtuple
from pathlib import Path

import cv2
import numpy as np
from numpy.random import rand

Pulse = namedtuple("Pulse", ["t0", "A", "sigma"])

OUTPUT_FRAMES_FOLDER = Path("./shaken_day_frames")
MAN_INPUT = Path("./dithered_man.png")
CUBE_INPUT = Path("./hypercube_frames")

SHAKED_CHANNELS = ["G", "B"]
SHAKE_AMPLITUDE = 2

pulses = [
    Pulse(45, 13, 8),
    Pulse(15, 10, 3),
]


man = cv2.imread(str(MAN_INPUT))
channel_mapping = {"R": 2, "G": 1, "B": 0}


def compose_affines(t1, t2):
    t1_extend = np.eye(3)
    t2_extend = np.eye(3)

    t1_extend[:2, :] = t1
    t2_extend[:2, :] = t2

    combined_t = t2_extend @ t1_extend

    return combined_t[:2, :]


def gaussian(t, t0, A, sigma):
    return A * np.exp(-((t - t0) ** 2) / (2 * sigma * sigma))


def shaking_amplitude_transform(t, pulses):
    amplitude = sum([gaussian(t, pulse.t0, pulse.A, pulse.sigma) for pulse in pulses])

    # scale_amp = np.random.rand() * 0.003 + 0.997
    row_disp_amplitude = amplitude * (rand() - 0.5)
    col_disp_amplitude = amplitude * (rand() - 0.5)

    transform = np.array([[1, 0, row_disp_amplitude], [0, 1, col_disp_amplitude]])

    return transform


def shake_the_world(img, t, pulses, shaked_channels, shake_amplitude):
    n_rows = img.shape[0]
    n_cols = img.shape[1]
    for ch in shaked_channels:
        row_disp = (rand() - 0.5) * shake_amplitude
        col_disp = (rand() - 0.5) * shake_amplitude

        noise_transform = np.array([[1, 0, col_disp], [0, 1, row_disp]])

        img[:, :, channel_mapping[ch]] = cv2.warpAffine(
            img[:, :, channel_mapping[ch]],
            compose_affines(noise_transform, shaking_amplitude_transform(t, pulses)),
            (n_cols, n_rows),
            borderMode=cv2.BORDER_REFLECT_101,
        )

    return img


for idx, input_cube_frame in enumerate(sorted(CUBE_INPUT.glob("frame_*.png"))):
    cube_scale = 0.23
    hypercube = cv2.imread(str(input_cube_frame))

    hypercube = cv2.resize(
        hypercube, None, fx=cube_scale, fy=cube_scale, interpolation=cv2.INTER_CUBIC
    )

    # invert so that the reference image is black. This also helps stoppint overflow
    # errors when we add the star field.
    man_ = man.copy()

    # NOTE: Where the cube end up is hard coded and depends a lot on the output of
    # `dither_man.py`
    offset_x, offset_y = 230, 0
    man_[
        offset_y : offset_y + hypercube.shape[0],
        offset_x : offset_x + hypercube.shape[1],
    ] = hypercube

    # NOTE: Finally trim a bit more from the top. Again strongly dependent on images
    man_ = man_[50:, :]

    man_ = shake_the_world(man_, idx, pulses, SHAKED_CHANNELS, SHAKE_AMPLITUDE)

    cv2.imwrite(str(OUTPUT_FRAMES_FOLDER / f"frame_{idx:03}.png"), man_)
