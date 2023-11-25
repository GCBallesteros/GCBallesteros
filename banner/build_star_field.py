from collections import namedtuple
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

BBox = namedtuple("BBox", ["top", "bottom", "left", "right"])
Star = namedtuple(
    "Star", ["blinking_freq", "blinking_phase", "intensity", "size", "row", "col"]
)

MASK = Path("./mask.png")
N_STARS = 200
BLUR_KERNEL_SIZE = 7
N_FRAMES = len(list(Path("./hypercube_frames").glob("*.png")))
OUTPUT_PATH = Path("./star_field_frames/")


def create_stars(
    n_stars: int,
    min_freq: float,
    max_freq: float,
    phase_std: float,
    out_shape: tuple[int, int],
) -> list[Star]:
    star_field_area = BBox(
        int(0.05 * out_shape[0]),
        int(0.95 * out_shape[0]),
        int(0.02 * out_shape[1]),
        int(0.98 * out_shape[1]),
    )

    star_positions = np.random.rand(n_stars, 2)
    star_positions *= np.array(
        (
            star_field_area.bottom - star_field_area.top,
            star_field_area.right - star_field_area.left,
        )
    ).astype(np.int64)

    star_positions += np.array((star_field_area.top, star_field_area.left))
    star_positions = star_positions.astype(np.int64)

    stars = [
        Star(
            np.random.rand() * (max_freq - min_freq) + min_freq,
            np.random.randn() * phase_std,
            np.random.rand(),
            np.random.rand(),
            pos[0],
            pos[1],
        )
        for pos in star_positions
    ]

    return stars


def make_star_frame(
    star: Star, out_shape: tuple[int, int], t: int
) -> npt.NDArray[np.float64]:
    single_star_frame = np.zeros(out_shape, dtype=np.float64)

    single_star_frame[star.row, star.col] = (
        np.cos(star.blinking_freq * t + star.blinking_phase) ** 2
    ) * star.intensity

    # As an optimization we only do the blur over the a star bounded in a tiny image
    # and then copy paste the patch into the output image
    cutout_size = 31
    half_cutout_size = int(cutout_size // 2)

    star_cutout = np.zeros((cutout_size,) * 2)
    star_cutout[half_cutout_size, half_cutout_size] = (
        np.cos(star.blinking_freq * t + star.blinking_phase) ** 2
    ) * star.intensity
    star_cutout = cv2.GaussianBlur(
        star_cutout,
        (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE),
        sigmaX=star.size,
        sigmaY=star.size,
    ).astype(np.float64)

    half_kernel = int(BLUR_KERNEL_SIZE // 2)

    single_star_frame[
        star.row - half_kernel : star.row + half_kernel,
        star.col - half_kernel : star.col + half_kernel,
    ] = star_cutout[
        half_cutout_size - half_kernel : half_cutout_size + half_kernel,
        half_cutout_size - half_kernel : half_cutout_size + half_kernel,
    ]

    return single_star_frame


mask: npt.NDArray = cv2.imread(str(MASK))[:, :, 0]
stars = create_stars(N_STARS, 0.05, 0.15, np.pi, mask.shape)


for frame_idx in range(N_FRAMES):
    star_field = np.zeros(mask.shape, dtype=np.float64)
    for star in stars:
        star_field = star_field + make_star_frame(star, mask.shape, frame_idx)

    # Renormalize, invert and cast to uint8
    star_field = star_field / np.max(star_field)
    star_field = 1 - star_field
    star_field *= 255
    star_field = star_field.astype(np.uint8)

    cv2.imwrite(str(OUTPUT_PATH / f"star_field_{frame_idx:03}.png"), star_field)
