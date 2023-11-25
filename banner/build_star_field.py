from collections import namedtuple
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt
from scipy.stats.qmc import PoissonDisk

Star = namedtuple(
    "Star",
    [
        "freq_weights",
        "freq_phases",
        "intensity",
        "size",
        "row",
        "col",
    ],
)

MASK = Path("./mask.png")
N_STARS = 250
POISSON_RADIUS = 0.05
WEIGHTS_RANDOM_FACTOR = 0.5
WEIGHTS_DECAY = 0.5
BLUR_KERNEL_SIZE = 7
N_FRAMES = len(list(Path("./hypercube_frames").glob("*.png")))
OUTPUT_PATH = Path("./star_field_frames/")
N_HARMONICS = 6

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
        | (star_positions[:, 1] < 0.05)
        | (star_positions[:, 1] > 0.95)
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
            np.random.rand(n_harmonics) * np.pi,
            np.random.rand(),
            np.random.rand(),
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
    cutout_size = 31
    half_cutout_size = int(cutout_size // 2)

    harmonic_freqs = (1 / period) * np.arange(n_harmonics)

    star_cutout = np.zeros((cutout_size,) * 2)
    # not 2 pi because the square doubles the freq
    star_cutout[half_cutout_size, half_cutout_size] = np.sum(
        # Fourier sum
        [
            (1 + np.cos(2 * np.pi * freq * t + freq_phase))
            * star.intensity
            * freq_weight
            for freq_weight, freq_phase, freq in zip(
                star.freq_weights, star.freq_phases, harmonic_freqs
            )
        ]
    )
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
stars = create_stars(
    N_STARS, mask.shape, N_HARMONICS, POISSON_RADIUS, WEIGHTS_RANDOM_FACTOR
)

for frame_idx in range(N_FRAMES):
    star_field = np.zeros(mask.shape, dtype=np.float64)
    for star in stars:
        star_field = star_field + make_star_frame(
            star, mask.shape, frame_idx, N_FRAMES, N_HARMONICS
        )

    # Renormalize, invert and cast to uint8
    star_field = 1 - star_field
    star_field *= 255
    star_field = star_field.astype(np.uint8)

    cv2.imwrite(str(OUTPUT_PATH / f"star_field_{frame_idx:03}.png"), star_field)
