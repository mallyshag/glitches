#!/usr/bin/env python

from glitches.colour import median_cut
from glitches.dithering import floyd_steinberg
from glitches.dithering import bayer, bayer_1
from PIL import Image


def main():
    image = Image.open("test.jpg")
    colours = median_cut(image, 16)
    outim = floyd_steinberg(image, colours, mode="RGB")
    outim.save("floyd.png")
    outim = bayer_1(image, colours)
    outim.save("bayer.png")

if __name__ == '__main__':
    main()
