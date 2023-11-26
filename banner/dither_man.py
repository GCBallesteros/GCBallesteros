import cv2
import numpy as np


class ditherModule:
    def dither(self, img, method="floyd-steinberg", resize=False):
        if resize:
            img = cv2.resize(
                img,
                (int(0.5 * (np.shape(img)[1])), int(0.5 * (np.shape(img)[0]))),
            )
        if method == "simple2D":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + (0.5 * err)
                    out[i + 1][j] = out[i + 1][j] + (0.5 * err)

            return out[1 : rows - 1, 1 : cols - 1]

        elif method == "floyd-steinberg":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 16) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((3 / 16) * err)
                    out[i + 1][j] = out[i + 1][j] + ((5 / 16) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((1 / 16) * err)

            return out[1 : rows - 1, 1 : cols - 1]

        elif method == "jarvis-judice-ninke":
            img = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(2, rows - 2):
                for j in range(2, cols - 2):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 48) * err)
                    out[i][j + 2] = out[i][j + 2] + ((5 / 48) * err)

                    out[i + 1][j - 2] = out[i + 1][j - 2] + ((3 / 48) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((5 / 48) * err)
                    out[i + 1][j] = out[i + 1][j] + ((7 / 48) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((5 / 48) * err)
                    out[i + 1][j + 2] = out[i + 1][j + 2] + ((3 / 48) * err)

                    out[i + 2][j - 2] = out[i + 2][j - 2] + ((1 / 48) * err)
                    out[i + 2][j - 1] = out[i + 2][j - 1] + ((3 / 48) * err)
                    out[i + 2][j] = out[i + 2][j] + ((5 / 48) * err)
                    out[i + 2][j + 1] = out[i + 2][j + 1] + ((3 / 48) * err)
                    out[i + 2][j + 2] = out[i + 2][j + 2] + ((1 / 48) * err)

            return out[2 : rows - 2, 2 : cols - 2]

        else:
            raise TypeError(
                'specified method does not exist. available methods = "simple2D", "floyd-steinberg(default)", "jarvis-judice-ninke"'
            )


def dither(img, method="floyd-steinberg", resize=False):
    dither_object = ditherModule()
    out = dither_object.dither(img, method, resize)
    return out


def resize_image(img, scale_ratio):
    img_resized = cv2.resize(
        img, None, fx=scale_ratio, fy=scale_ratio, interpolation=cv2.INTER_CUBIC
    )

    return img_resized


def crop_image(img, left, bottom):
    return img[:-bottom, left:]


if __name__ == "__main__":
    img = cv2.imread("./assets/man_horizon_wider.png")

    mask = (img.sum(axis=2) != 0).astype(np.uint8)
    # Clean up a bit the mask
    mask = cv2.dilate(mask, np.ones((3, 3)))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    scale_ratio = 0.7
    img_resized = resize_image(img, scale_ratio)
    mask_resized = resize_image(mask, scale_ratio)

    dithered_img = dither(img_resized, "jarvis-judice-ninke")

    # Remove extraneous image that we don't want
    dithered_img = crop_image(dithered_img, 400, 170)
    mask_resized = crop_image(mask_resized, 400, 170)

    # Top pad the image to get some space above the man to place the hypercube
    expanded_img = np.zeros(
        (
            int(dithered_img.shape[0] * 2.0),
            int(dithered_img.shape[1]),
        ),
        dtype=dithered_img.dtype,
    )
    expanded_mask = np.zeros(
        (
            int(mask_resized.shape[0] * 2.0),
            int(mask_resized.shape[1]),
        ),
        dtype=dithered_img.dtype,
    )

    y_offset = expanded_img.shape[0] - dithered_img.shape[0]
    expanded_img[
        y_offset : y_offset + dithered_img.shape[0], : dithered_img.shape[1]
    ] = dithered_img
    expanded_mask[
        y_offset : y_offset + mask_resized.shape[0], : mask_resized.shape[1]
    ] = mask_resized

    # invert the image so that image is actually in black
    expanded_img = 255 * (1 - expanded_img.astype(np.int8))
    cv2.imwrite("./assets/dithered_man.png", expanded_img)
    cv2.imwrite("./assets/mask.png", expanded_mask)
