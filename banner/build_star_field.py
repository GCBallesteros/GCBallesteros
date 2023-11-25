from collections import namedtuple
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt
from scipy.stats.qmc import PoissonDisk
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

np.random.seed(123)

Star = namedtuple(
    "Star",
    [
        "freq_weights",
        "freq_phases",
        "min_intensity",
        "max_intensity",
        "size",
        "row",
        "col",
    ],
)

MASK = Path("./mask.png")
N_STARS = 150
POISSON_RADIUS = 0.05
WEIGHTS_RANDOM_FACTOR = 0.3
WEIGHTS_DECAY = 0.5
BLUR_KERNEL_SIZE = 7
N_FRAMES = len(list(Path("./hypercube_frames").glob("*.png")))
OUTPUT_PATH = Path("./star_field_frames/")
N_HARMONICS = 4

# TODO: Missing parameters for exponential distro


def create_stars(
    n_stars: int,
    out_shape: tuple[int, int],
    n_harmonics: int,
    poisson_disk_radius: float,
    weights_randomness: float,
) -> list[Star]:
    engine = PoissonDisk(d=2, radius=poisson_disk_radius, seed=42, optimization="lloyd")
    star_positions = engine.random(n_stars)

    msk_near_border = (
        (star_positions[:, 0] < 0.05)
        | (star_positions[:, 0] > 0.95)
        | (star_positions[:, 1] < 0.03)
        | (star_positions[:, 1] > 0.97)
    )

    star_positions = star_positions[~msk_near_border]
    star_positions[:, 0] *= out_shape[0]
    star_positions[:, 1] *= out_shape[1]
    star_positions = star_positions.astype(np.int64)

    # Generate frequency that is perfectly periodic
    def make_random_normalized_vec(n):
        arr = 1 + (np.random.rand(n) - 0.5) * weights_randomness
        # give more weight to lower freqs
        arr = arr * np.exp(-np.arange(n) * WEIGHTS_DECAY)
        # normalize
        arr /= arr.sum()
        return arr

    stars = [
        Star(
            make_random_normalized_vec(n_harmonics),
            np.random.rand(n_harmonics) * 2 * np.pi,
            0.2,
            1 - np.random.rand() * 0.6,
            np.random.rand() * 0.8 + 0.2,
            pos[0],
            pos[1],
        )
        for pos in star_positions
    ]

    return stars


def make_star_frame(
    star: Star, out_shape: tuple[int, int], t: int, period: int, n_harmonics: int
) -> npt.NDArray[np.float64]:
    single_star_frame = np.zeros(out_shape, dtype=np.float64)

    # As an optimization we only do the blur over the a star bounded in a tiny image
    # and then copy paste the patch into the output image
    cutout_size = 91
    half_cutout_size = int(cutout_size // 2)

    harmonic_freqs = (1 / period) * np.arange(1, n_harmonics + 1)
    freq_weights = np.array(star.freq_weights)
    freq_phases = np.array(star.freq_phases)

    star_cutout = np.zeros((cutout_size,) * 2, dtype=np.float64)
    dynamic_range = star.max_intensity - star.min_intensity

    star_cutout[half_cutout_size, half_cutout_size] = np.sum(
        (
            (np.cos(2 * np.pi * harmonic_freqs * t + freq_phases) + 1)
            * 0.5  # at this points we have a 0 to 1 function
            * dynamic_range  # now a 0 to dynamic range function
            + star.min_intensity  # rise the minimum
        )
        * freq_weights
    )

    blurred_star = gaussian_filter(star_cutout, star.size, mode="constant", radius=5)

    half_kernel = int(BLUR_KERNEL_SIZE // 2)

    single_star_frame[
        star.row - half_kernel : star.row + half_kernel,
        star.col - half_kernel : star.col + half_kernel,
    ] = blurred_star[
        half_cutout_size - half_kernel : half_cutout_size + half_kernel,
        half_cutout_size - half_kernel : half_cutout_size + half_kernel,
    ]

    return single_star_frame


mask: npt.NDArray = cv2.imread(str(MASK))[:, :, 0]
stars = create_stars(
    N_STARS, mask.shape, N_HARMONICS, POISSON_RADIUS, WEIGHTS_RANDOM_FACTOR
)


star_field_frames = np.zeros((N_FRAMES, *mask.shape), dtype=np.float64)
for frame_idx in range(N_FRAMES):
    for star in stars:
        new_star = make_star_frame(star, mask.shape, frame_idx, N_FRAMES, N_HARMONICS)
        star_field_frames[frame_idx, :, :] += new_star

# filter out zeros to not completely destroy the quantile
max_frames = np.quantile(star_field_frames[star_field_frames != 0], 0.995)

# normalize, clip, invert and cast to uint8 (leave a safety oneoff)
star_field_frames = np.clip(star_field_frames, 0, max_frames) / max_frames
star_field_frames = (star_field_frames * 255).astype(np.uint8)

for frame_idx in range(N_FRAMES):
    cv2.imwrite(
        str(OUTPUT_PATH / f"star_field_{frame_idx:03}.png"),
        star_field_frames[frame_idx, :, :],
    )
