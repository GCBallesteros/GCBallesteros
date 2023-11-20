from pathlib import Path

import cv2
import matplotlib.pyplot as plt

OUTPUT_FRAMES_FOLDER = Path("./horizon_man_looking_hypercube")
MAN_INPUT = Path("./dithered_man.png")
CUBE_INPUT = Path("./hypercube_frames")

man = cv2.imread(str(MAN_INPUT))

for idx, input_cube_frame in enumerate(sorted(CUBE_INPUT.glob("frame_*.png"))):
    hypercube = cv2.imread(str(input_cube_frame))
    hypercube = cv2.resize(
        hypercube, None, fx=0.23, fy=0.23, interpolation=cv2.INTER_CUBIC
    )
    man_ = man.copy()
    offset_x, offset_y = 230, 0
    man_[
        offset_y : offset_y + hypercube.shape[0],
        offset_x : offset_x + hypercube.shape[1],
    ] = hypercube

    # Finally trim a bit more from the top
    man_ = man_[50:, :]
    cv2.imwrite(str(OUTPUT_FRAMES_FOLDER / f"frame_{idx:03}.png"), man_)
