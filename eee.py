#!/usr/bin/env python

from glitches.dithering import bayer
from glitches.colour import mono_palette, hue_palette, replace_colours
from glitches.colour import quantize, swatch
from PIL import Image
import random


def random_hues(num):
    return [random.random() for i in range(num)]


def comp_colours(num):
    r = True
    last_hue = -1
    hues = []
    for i in range(num):
        if r:
            r = False
            last_hue = random.random()
            hues.append(random.random())
        else:
            r = True
            hues.append((last_hue + 0.5) % 1.0)
    return hues


def comp_4():
    a = random.random()
    b = random.random()
    c = (b + 0.5) % 1.0
    d = (a + 0.5) % 1.0
    return (a, b, c, d)


def comp_4b():
    a = random.random()
    b = (a + random.uniform(-0.2, 0.2)) % 1.0
    c = (a + 0.5) % 1.0
    d = (c + random.uniform(-0.2, 0.2)) % 1.0
    return (a, b, c, d)


def comp_4c():
    a = random.random()
    b = (a + random.uniform(-0.1, 0.1)) % 1.0
    c = (b + random.uniform(-0.1, 0.1)) % 1.0
    d = (b + random.uniform(0.2, 0.4)) % 1.0
    return (a, b, c, d)


def main():
    image = Image.open("test.jpg")

    # Create target palette
    target_palette = hue_palette(comp_4c())
    swatch(target_palette, "hues.png")
    num_colours = len(target_palette)

    # Prequantize
    image = quantize(image, mono_palette(8))

    # Create monochrome palette
    colours = mono_palette(num_colours)

    # Dither image based on monochrome palette
    dithim = bayer(image, colours, matrix=2).convert("RGB")

    # Replace colours in image with target palette
    outim = replace_colours(dithim, colours, target_palette)

    # Save dithered coloured image
    outim.save("palette_test.png")

if __name__ == '__main__':
    main()
