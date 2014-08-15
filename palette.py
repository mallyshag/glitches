#!/usr/bin/env python

from glitches.dithering import floyd_steinberg
from glitches.colour import mono_palette, colour_palette
from PIL import Image
import numpy as np


def replace_colours(image, pal_a, pal_b):
    def hash_col(col):
        r, g, b = col
        hcol = (int(r) << 16) + (int(g) << 8) + int(b)
        return hcol
    # Prepare the palettes
    from_pal = {hash_col(pal_a[i]):i for i in range(len(pal_a))}
    to_pal = {i:pal_b[i] for i in range(len(pal_b))}

    im_array = np.array(image)
    im_array = np.reshape(im_array, (im_array.shape[0] * im_array.shape[1], 3))
    for p in xrange(im_array.shape[0]):
        old_col = from_pal[hash_col(im_array[p])]
        new_col = to_pal[old_col]
        im_array[p] = new_col
    im_array = np.reshape(im_array, (image.size[1], image.size[0], 3))
    return Image.fromarray(im_array)


def main():
    image = Image.open("test.jpg")

    num_colours = 16

    # Create monochrome palette
    colours = mono_palette(num_colours)

    # Dither image based on monochrome palette
    dithim = floyd_steinberg(image, colours, mode="RGB")

    # Map fancy colours to aforementioned palette
    fancy_colours = colour_palette((0, 0, 255), (255, 255, 255), num_colours)

    # Replace colours in dithered image
    outim = replace_colours(dithim, colours, fancy_colours)

    # Save dithered coloured image
    outim.save("palette_test.png")

if __name__ == '__main__':
    main()
