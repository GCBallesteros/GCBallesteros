from pathlib import Path

import cv2
import numpy as np

OUTPUT_FRAMES_FOLDER = Path("./horizon_man_looking_hypercube")
MAN_INPUT = Path("./dithered_man.png")
CUBE_INPUT = Path("./hypercube_frames")
STAR_FRAMES = Path("./star_field_frames")
MASK_FILE = "./mask.png"

man = cv2.imread(str(MAN_INPUT))


for idx, input_cube_frame in enumerate(sorted(CUBE_INPUT.glob("frame_*.png"))):
    cube_scale = 0.23
    hypercube = cv2.imread(str(input_cube_frame))
    star_mask = (cv2.imread(MASK_FILE) == 0).astype(np.uint8)
    star_field = cv2.imread(str(STAR_FRAMES / f"star_field_{idx:03}.png"))

    hypercube = cv2.resize(
        hypercube, None, fx=cube_scale, fy=cube_scale, interpolation=cv2.INTER_CUBIC
    )
    man_ = man.copy()

    # NOTE: Where the cube end up is hard coded and depends a lot on the output of
    # `dither_man.py`
    offset_x, offset_y = 230, 0
    man_[
        offset_y : offset_y + hypercube.shape[0],
        offset_x : offset_x + hypercube.shape[1],
    ] = hypercube
    man_ += star_field * star_mask

    # NOTE: Finally trim a bit more from the top. Again strongly dependent on images
    man_ = man_[50:, :]
    cv2.imwrite(str(OUTPUT_FRAMES_FOLDER / f"frame_{idx:03}.png"), man_)
