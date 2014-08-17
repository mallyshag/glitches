#!/usr/bin/env python

from glitches.colour import median_cut, mono_palette
from glitches.dithering import floyd_steinberg
from glitches.dithering import bayer
from PIL import Image


def main():
    num_colours = 4

    image = Image.open("test.jpg")
    colours = median_cut(image, num_colours)
    outim = floyd_steinberg(image, colours, mode="RGB")
    outim.save("floyd_RGB.png")

    mono = mono_palette(num_colours)
    outim = floyd_steinberg(image, mono, mode="MONO")
    outim.save("floyd_MONO.png")

    outim = floyd_steinberg(image, mode="MONO")
    outim.save("floyd_BW.png")

    m = 8

    outim = bayer(image, matrix=m)
    outim.save("bayer_BW.png")

    outim = bayer(image, mono, matrix=m)
    outim.save("bayer_MONO.png")

if __name__ == '__main__':
    main()
