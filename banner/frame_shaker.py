from pathlib import Path

import cv2
import numpy as np

OUTPUT_FRAMES_FOLDER = Path("./shaken_day_frames")
MAN_INPUT = Path("./dithered_man.png")
CUBE_INPUT = Path("./hypercube_frames")

SHAKED_CHANNELS = ["G", "B"]
SHAKE_AMPLITUDE = 1.5


man = cv2.imread(str(MAN_INPUT))
channel_mapping = {"R": 2, "G": 1, "B": 0}


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

    # At this point we want to add a little shake. We will do it via a displacement
    # only affine transformation
    n_rows = man_.shape[0]
    n_cols = man_.shape[1]
    for ch in SHAKED_CHANNELS:
        row_disp = (np.random.rand() - 0.5) * 2 * SHAKE_AMPLITUDE
        col_disp = (np.random.rand() - 0.5) * 2 * SHAKE_AMPLITUDE

        noise_transform = np.array([[1, 0, row_disp], [0, 1, col_disp]])

        man_[:, :, channel_mapping[ch]] = cv2.warpAffine(
            man_[:, :, channel_mapping[ch]],
            noise_transform,
            (n_cols, n_rows),
            borderMode=cv2.BORDER_REFLECT_101,
        )

    cv2.imwrite(str(OUTPUT_FRAMES_FOLDER / f"frame_{idx:03}.png"), man_)
