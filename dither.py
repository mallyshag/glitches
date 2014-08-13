#!/usr/bin/env python

from glitches.colour import median_cut
import numpy as np
from scipy.weave import inline
from scipy.weave import converters
from PIL import Image


def dither_l(image, pal):
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


def dither(image, pal):
    """ Floyd-Steinberg dithering using a palette. """
    pal_array = np.array(pal, dtype=np.double)
    im_array = np.array(image, dtype=np.double)

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


def main():
    image = Image.open("test.jpg").convert("RGB")
    colours = median_cut(image, 16)
    outim = dither(image, colours)
    outim.save("dither_test.jpg")

if __name__ == '__main__':
    main()
