#!/usr/bin/env python

from glitches.colour import median_cut
from glitches.dithering import floyd_steinberg
from PIL import Image


def main():
    image = Image.open("test.jpg")
    colours = median_cut(image, 16)
    outim = floyd_steinberg(image, colours, mode="RGB")
    outim.save("dither_test.jpg")

if __name__ == '__main__':
    main()
