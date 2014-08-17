import numpy as np
from scipy.weave import inline
from scipy.weave import converters
from PIL import Image


def floyd_steinberg_mono(image, palette=None):
    """ Monochrome Floyd-Steinberg dithering """
    if palette is None:
        pal_array = np.array([])
        nc = 0  # noqa
    else:
        pal_array = np.array(palette, dtype=np.double)
        nc = pal_array.shape[0]  # noqa

    im_array = np.array(image.convert('L'), dtype=np.double)
    ny, nx = im_array.shape  # noqa

    code = """
    int col_idx;
    double nearest, tmp, dist;
    double quant_error, old_value, new_value;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            // Clamp Colour
            old_value = im_array(y, x);
            old_value = old_value < 0 ? 0 : old_value;
            old_value = old_value > 255 ? 255 : old_value;
            im_array(y, x) = old_value;

            if (nc == 0)
            {
                new_value = im_array(y, x) <= 128? 0 : 255;
            }
            else
            {
                col_idx = -1;
                nearest = -1;


                // Find Nearest Colour
                for (int c=0; c<nc; c++)
                {
                    dist = 0;
                    tmp = im_array(y, x) - pal_array(c);
                    dist += tmp * tmp;
                    if (col_idx == -1 || dist < nearest)
                    {
                        col_idx = c;
                        nearest = dist;
                    }
                }
                new_value = pal_array(col_idx);
            }

            // Set colour
            old_value = im_array(y, x);
            quant_error = old_value - new_value;
            im_array(y, x) = new_value;

            // Error diffusion
            if (x < nx - 1)
            {
                im_array(y, x+1) += quant_error * (7.0/16.0);
            }
            if (y < ny - 1)
            {
                if (x > 0)
                {
                    im_array(y+1, x-1) += quant_error * (3.0/16.0);
                }
                im_array(y+1, x) += quant_error * (5.0/16.0);
                if (x < nx - 1)
                {
                    im_array(y+1, x+1) += quant_error * (1.0/16.0);
                }
            }
        }
    }
    """
    inline(code, ['im_array', 'pal_array', 'nx', 'ny', 'nc'],
           type_converters=converters.blitz)

    return Image.fromarray(im_array.astype(np.uint8))


def floyd_steinberg_rgb(image, pal):
    """ Floyd-Steinberg dithering using a palette. """
    pal_array = np.array(pal, dtype=np.double)
    im_array = np.array(image.convert('RGB'), dtype=np.double)

    ny, nx, _ = im_array.shape  # noqa
    nc = pal_array.shape[0]  # noqa

    code = """
    int col_idx;
    double nearest, tmp, dist;
    double quant_error, old_value, new_value;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            col_idx = -1;
            nearest = -1;

            // Clamp Colour
            for (int band=0; band < 3; band++)
            {
                old_value = im_array(y, x, band);
                old_value = old_value < 0 ? 0 : old_value;
                old_value = old_value > 255 ? 255 : old_value;
                im_array(y, x, band) = old_value;
            }

            // Find Nearest Colour
            for (int c=0; c<nc; c++)
            {
                dist = 0;
                for (int band=0; band < 3; band++)
                {
                    tmp = im_array(y, x, band) - pal_array(c, band);
                    dist += tmp * tmp;
                }
                if (col_idx == -1 || dist < nearest)
                {
                    col_idx = c;
                    nearest = dist;
                }
            }

            // Set colour
            for (int band = 0; band < 3; band++)
            {
                old_value = im_array(y, x, band);
                new_value = pal_array(col_idx, band);
                quant_error = old_value - new_value;
                im_array(y, x, band) = new_value;

                // Error diffusion
                if (x < nx - 1)
                {
                    im_array(y, x+1, band) += quant_error * (7.0/16.0);
                }
                if (y < ny - 1)
                {
                    if (x > 0)
                    {
                        im_array(y+1, x-1, band) += quant_error * (3.0/16.0);
                    }
                    im_array(y+1, x, band) += quant_error * (5.0/16.0);
                    if (x < nx - 1)
                    {
                        im_array(y+1, x+1, band) += quant_error * (1.0/16.0);
                    }
                }
            }
        }
    }
    """
    inline(code, ['im_array', 'pal_array', 'nx', 'ny', 'nc'],
           type_converters=converters.blitz)

    return Image.fromarray(im_array.astype(np.uint8))


def floyd_steinberg(image, palette=None, mode="RGB"):
    if mode == "RGB":
        if palette is None:
            return None
        return floyd_steinberg_rgb(image, palette)
    elif mode == "MONO":
        return floyd_steinberg_mono(image, palette)
    else:
        return None


# Bayer/Ordered dithering code


tm2x2 = [1, 3,
         4, 2]

tm3x3 = [3, 7, 4,
         6, 1, 9,
         2, 8, 5]

tm4x4 = [1, 9, 3, 11,
         13, 5, 15, 7,
         4, 12, 2, 10,
         16, 8, 14, 6]

tm8x8 = [1, 49, 13, 61, 4, 52, 16, 64,
         33, 17, 45, 29, 36, 20, 48, 32,
         9, 57, 5, 53, 12, 60, 8, 56,
         41, 25, 37, 21, 44, 28, 40, 24,
         3, 51, 15, 63, 2, 50, 14, 62,
         35, 19, 47, 31, 34, 18, 46, 30,
         11, 59, 7, 55, 10, 58, 6, 54,
         43, 27, 39, 23, 42, 26, 38, 22]


def bayer_mono(image, palette=None, matrix=4):
    if matrix == 2:
        bayer = tm2x2
    elif matrix == 3:
        bayer = tm3x3
    elif matrix == 4:
        bayer = tm4x4
    elif matrix == 8:
        bayer = tm8x8
    else:
        return None

    if palette is None:
        pal_array = np.array([])
        nc = 2  # noqa
        bw = True  # noqa
    else:
        pal_array = np.array(palette, dtype=np.double)
        nc = pal_array.shape[0]  # noqa
        bw = False  # noqa

    im_array = np.array(image.convert('L'), dtype=np.double)

    # Calculate level gap
    gap = 255.0 / (nc - 1)

    # Setup bayer matrix
    bmatrix = np.array(bayer, dtype=np.double).reshape((matrix, matrix))
    bmatrix *= gap
    bmatrix /= len(bayer)
    bmatrix -= gap / 2.0

    # Tile bayer matrix
    bmatrix = np.tile(bmatrix, ((im_array.shape[0] / bmatrix.shape[0]) + 1,
                                (im_array.shape[1] / bmatrix.shape[1]) + 1))
    bmatrix = bmatrix[:im_array.shape[0], :im_array.shape[1]]

    # Add Bayer Matrix
    im_array += bmatrix

    # Find nearest pixels
    ny, nx = im_array.shape  # noqa

    code = """
    int col_idx;
    double nearest, tmp, dist;
    double col;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            if (bw == true)
            {
                col = im_array(y, x);
                col = col < 128 ? 0 : 255;
            }
            else
            {
                col = im_array(y, x);
                col = col > 255? 255 : col;
                col = col < 0? 0: col;

                col_idx = -1;
                nearest = -1;

                // Find Nearest Colour
                for (int c=0; c<nc; c++)
                {
                    dist = 0;
                    tmp = col - pal_array(c);
                    dist += tmp * tmp;
                    if (col_idx == -1 || dist < nearest)
                    {
                        col_idx = c;
                        nearest = dist;
                    }
                }
                col = pal_array(col_idx);
            }
            im_array(y, x) = col;
        }
    }
    """
    inline(code, ['im_array', 'pal_array', 'nx', 'ny', 'nc', 'bw'],
           type_converters=converters.blitz)
    return Image.fromarray(im_array.astype(np.uint8))

bayer = bayer_mono
