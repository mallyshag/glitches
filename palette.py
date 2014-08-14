#!/usr/bin/env python

from glitches.dithering import floyd_steinberg
from PIL import Image
import numpy as np
import colorsys


def create_mono_palette(num_colours):
    step = 255 / (num_colours - 1)
    palette = [i * step for i in range(num_colours)]
    palette = [(l, l, l) for l in palette]
    return palette


def create_colour_palette(colour_a, colour_b, steps):
    from_colour = colorsys.rgb_to_hsv(*colour_a)
    to_colour = colorsys.rgb_to_hsv(*colour_b)
    print from_colour
    print to_colour

    hstep = (to_colour[0] - from_colour[0]) / (steps - 1)
    sstep = (to_colour[1] - from_colour[1]) / (steps - 1)
    vstep = (to_colour[2] - from_colour[2]) / (steps - 1)

    if to_colour[0] == 0 and to_colour[1] == 0:
        hstep =  0;
    
    palette = []
    for i in range(steps):
        h = from_colour[0] + i * hstep
        s = from_colour[1] + i * sstep
        v = from_colour[2] + i * vstep
        palette.append(colorsys.hsv_to_rgb(h, s, v))
    return palette


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
    colours = create_mono_palette(num_colours)

    # Dither image based on monochrome palette
    dithim = floyd_steinberg(image, colours, mode="RGB")

    # Map fancy colours to aforementioned palette
    fancy_colours = create_colour_palette((0, 0, 255), (255, 255, 255), num_colours)

    # Replace colours in dithered image
    outim = replace_colours(dithim, colours, fancy_colours)

    # Save dithered coloured image
    outim.save("palette_test.png")

if __name__ == '__main__':
    main()
