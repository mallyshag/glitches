#!/usr/bin/env python

from PIL import Image
from glitches.colour import median_cut, recolour


def main():
    im = Image.open("test.jpg")

    # Extract optimized palette
    palette = median_cut(im, 4)

    # Recolour image
    outim = recolour(im, palette)
    outim.save("test_out.jpg")


if __name__ == '__main__':
    main()
