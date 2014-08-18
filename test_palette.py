#!/usr/bin/env python

from glitches.colour import swatch
from glitches.colour import hue_palette


def main():
    # num_colours = 16

    # Generate palette
    # palette = mono_palette(num_colours)

    # Colour palette
    # palette = colour_palette((0, 255, 255), (255, 0, 255), num_colours)

    # Fancy Palette
    palette = hue_palette((0, 0.25, 0.5, 0.75))

    # Create image from palette
    swatch(palette, "swatch.png")


if __name__ == '__main__':
    main()
