#!/usr/bin/env python

import glitches.dithering as gl_d
import glitches.colour as gl_c
import glitches.util as gl_u
from PIL import Image, ImageOps, ImageColor
from argparse import ArgumentParser
from operator import itemgetter
import math
import numpy as np

ZX_BASIC = ["#000000", "#0000CD", "#CD0000", "#CD00CD",
             "#00CD00", "#00CDCD", "#CDCD00", "#CDCDCD"]
ZX_BASIC = [ImageColor.getrgb(c) for c in ZX_BASIC]

ZX_BRIGHT = ["#000000", "#0000FF", "#FF0000", "#FF00FF",
             "#00FF00", "#00FFFF", "#FFFF00", "#FFFFFF"]
ZX_BRIGHT = [ImageColor.getrgb(c) for c in ZX_BRIGHT]

ZX_HEX = ZX_BASIC + ZX_BRIGHT


def colour_dist(a, b):
    dist = 0
    for aa, bb in zip(a, b):
        dist += (aa - bb) ** 2
    return math.sqrt(dist)


def nearest_colour(colour, palette):
    nearest = -1
    near_dist = -1
    for i in range(len(palette)):
        c = palette[i]
        c_dist = colour_dist(colour, c)
        if near_dist == -1 or c_dist < near_dist:
            near_dist = c_dist
            nearest = i
    return palette[nearest], near_dist, nearest


def match_colours(colours, palette):
    # XXX Dreadful, absolutely dreadful
    if len(colours) == 1:
        am, ams, amidx = nearest_colour(colours[0], palette)
        return [am], ams
    else:
        a, b = colours

        # Colour A
        am, ams, amidx = nearest_colour(a, palette)

        # Colour B
        palette_2 = palette[:amidx] + palette[amidx + 1:]
        bm, bms, bmidx = nearest_colour(b, palette_2)

        return [am, bm], ams + bms


def attribute_block(image, x, y):
    # Copy and load block
    block = image.crop((x, y, x + 8, y + 8))
    block.load()

    # Get top colours in block
    cols = gl_c.median_cut(block, 2)

    # Match to basic and bright palettes
    a_cols, a_score = match_colours(cols, ZX_BASIC)
    b_cols, b_score = match_colours(cols, ZX_BRIGHT)

    if (a_score < b_score):
        return gl_d.floyd_steinberg(block, a_cols)
    else:
        return gl_d.floyd_steinberg(block, b_cols)


def main():
    parser = ArgumentParser()
    parser.add_argument("inage", metavar='INPUT', type=str)
    parser.add_argument("outage", metavar='OUTPUT', type=str)
    parser.add_argument("-d", "--dither", type=str, default="BAYER")
    parser.add_argument("-m", "--matrix", type=int, default=-2)
    parser.add_argument("-e", "--equalize", action="store_true", default=False)
    args = parser.parse_args()

    image = Image.open(args.inage)

    if args.equalize:
        image = ImageOps.equalize(image)

    # Resize Image
    image = gl_u.resize(image, 256, 192)

    # Pre-quantize image
    #image = gl_c.quantize(image, gl_c.median_cut(image, 32))
    # image = gl_d.floyd_steinberg(image, ZX_HEX)
    # image.save(args.outage)
    # exit()

    # Quantize
    # outim = gl_c.quantize(image, palette)
    outim = Image.new("RGB", image.size, "black")
    
    for x in range(256 >> 3):
        for y in range(192 >> 3):
            block = attribute_block(image, x << 3, y << 3)
            outim.paste(block, (x << 3, y << 3))
    # Dither image based on monochrome palette
    #if args.dither.upper() == "FS":
        #dithim = gl_d.floyd_steinberg(image, monos, mode="MONO").convert("RGB")
    #elif args.dither.upper() == "BAYER":
        #dithim = gl_d.bayer(image, monos, matrix=args.matrix).convert("RGB")
    #else:
        #dithim = gl_d.bayer(image, monos, matrix=args.matrix).convert("RGB")

    # Save zx-ified
    outim.save(args.outage)

if __name__ == '__main__':
    main()
