import numpy as np
from scipy.weave import inline
from scipy.weave import converters
from PIL import Image


def floyd_steinberg_1bit(image):
    """ Floyd-Steinberg dithering using 1-bit colour. """
    im_array = np.array(image.convert('L'), dtype=np.double)
    ny, nx = im_array.shape  # noqa

    code = """
    double col;
    double quant_error;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            col = im_array(y, x) <= 128? 0 : 255;

            quant_error = im_array(y, x) - col;
            im_array(y, x) = col;

            if (x < nx - 1)
            {
                im_array(y, x + 1) += quant_error * (7.0/16.0);
            }
            if (y < ny - 1)
            {
                if (x > 0)
                {
                    im_array(y + 1, x - 1) += quant_error * (3.0/16.0);
                }
                im_array(y + 1, x) += quant_error * (5.0/16.0);
                if (x < nx - 1)
                {
                    im_array(y + 1, x + 1) += quant_error * (1.0/16.0);
                }
            }
        }
    }
    """
    inline(code, ['im_array', 'nx', 'ny'],
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
    elif mode == "1":
        return floyd_steinberg_1bit(image)
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


def bayer(image, palette):
    # Create Image Array
    im_array = np.array(image.convert('RGB'), dtype=np.double)
    pal_array = np.array(palette, dtype=np.double)

    # Resize Bayer Matrix to Size of Array
    bmatrix = np.array(bayer, dtype=np.double).reshape((4, 4))
    #bmatrix = np.array(bayer).reshape((8, 8))
    #bmatrix *= 255.0/((len(bayer) + 1) * len(palette))
    bmatrix *= 255.0/17.0
    bmatrix /= 4.0
    print bmatrix
    bmatrix = np.tile(bmatrix, ((im_array.shape[0] / bmatrix.shape[0]) + 1,
                                (im_array.shape[0] / bmatrix.shape[1]) + 1))
    bmatrix = bmatrix[:im_array.shape[0], :im_array.shape[1]]

    # Add Bayer Matrix
    im_array[:,:,0] += bmatrix
    im_array[:,:,1] += bmatrix
    im_array[:,:,2] += bmatrix

    # Find nearest pixels
    ny, nx, _ = im_array.shape  # noqa
    nc = pal_array.shape[0]  # noqa

    code = """
    int col_idx;
    double nearest, tmp, dist, col;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            col_idx = -1;
            nearest = -1;

            // Find Nearest Colour
            for (int c=0; c<nc; c++)
            {
                dist = 0;
                for (int band=0; band < 3; band++)
                {
                    col = im_array(y, x, band);
                    col = col < 0? 0 : col;
                    col = col > 255? 255: col;
                    tmp = col - pal_array(c, band);
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
                im_array(y, x, band) = pal_array(col_idx, band);
            }
        }
    }
    """
    inline(code, ['im_array', 'pal_array', 'nx', 'ny', 'nc'],
           type_converters=converters.blitz)
    return Image.fromarray(im_array.astype(np.uint8))


def bayer_1(image, palette):
    # Create Image Array
    im_array = np.array(image.convert('L'), dtype=np.double)

    # Resize Bayer Matrix to Size of Array
    #bmatrix = np.array(bayer, dtype=np.double).reshape((4, 4))
    bmatrix = np.array(bayer).reshape((8, 8))
    bmatrix *= 255.0/(len(bayer) + 1.0)
    bmatrix = np.tile(bmatrix, ((im_array.shape[0] / bmatrix.shape[0]) + 1,
                                (im_array.shape[0] / bmatrix.shape[1]) + 1))
    bmatrix = bmatrix[:im_array.shape[0], :im_array.shape[1]]

    # Add Bayer Matrix
    im_array += bmatrix

    # Find nearest pixels
    ny, nx = im_array.shape  # noqa

    code = """
    double col;
    for (int y = 0; y < ny; y++)
    {
        for (int x = 0; x < nx; x++)
        {
            col = floor(im_array(y, x) / 2.0);
            col = col < 129 ? 0 : 255; 
            im_array(y, x) = col;
        }
    }
    """
    inline(code, ['im_array', 'nx', 'ny'],
           type_converters=converters.blitz)
    return Image.fromarray(im_array.astype(np.uint8))
