#!/usr/bin/env python

import glitches.dithering as gl_d
import glitches.colour as gl_c
import glitches.util as gl_u
from PIL import Image, ImageOps
import random
from argparse import ArgumentParser


def random_hues(num):
    return gl_c.hue_palette([random.random() for i in range(num)])


def comp_colours(spread=0.1, c_min=0.2, c_max=0.4):
    a = random.random()
    b = (a + random.uniform(-spread, spread)) % 1.0
    c = (b + random.uniform(-spread, spread)) % 1.0
    d = (b + random.uniform(c_min, c_max)) % 1.0
    return (a, b, c, d)


def main():
    parser = ArgumentParser()
    parser.add_argument("inage", metavar='INPUT', type=str)
    parser.add_argument("outage", metavar='OUTPUT', type=str)
    parser.add_argument("-p", "--palette", type=str, default="AUTO")
    parser.add_argument("-d", "--dither", type=str, default="BAYER")
    parser.add_argument("-iw", "--width", type=int, default=-1)
    parser.add_argument("-ih", "--height", type=int, default=-1)
    parser.add_argument("-m", "--matrix", type=int, default=-2)
    parser.add_argument("-e", "--equalize", action="store_true", default=False)
    args = parser.parse_args()

    image = Image.open(args.inage)

    if args.equalize:
        image = ImageOps.equalize(image)

    # Create target palette
    if args.palette.upper() == "GB":
        out_palette = gl_c.GAMENIPPER
    elif args.palette.upper() == "ISS":
        out_palette = gl_c.LOVE
    elif args.palette.upper() == "AUTO":
        out_palette = gl_c.hue_palette(comp_colours())
    elif args.palette.upper() == "COMP":
        out_palette = gl_c.hue_palette(comp_colours(c_min=-0.1, c_max=0.1))
    elif args.palette.upper() == "WHITE":
        out_palette = [(0, 0, 0)]
        out_palette += gl_c.hue_palette((random.random(),), low=128)
        out_palette.append((255, 255, 255))
    elif args.palette.upper() == "MONO":
        out_palette = gl_c.mono_palette(4)
    else:
        out_palette = gl_c.GAMENIPPER
    num_colours = len(out_palette)

    # Resize Image
    bgcolor = "rgb(%d, %d, %d)" % out_palette[0]
    image = gl_u.resize(image, args.width, args.height)
    
    # Prequantize
    image = gl_c.quantize(image, gl_c.mono_palette(num_colours * 4))

    # Create monochrome palette for quantization
    monos = gl_c.mono_palette(num_colours)

    # Dither image based on monochrome palette
    if args.dither.upper() == "FS":
        dithim = gl_d.floyd_steinberg(image, monos, mode="MONO").convert("RGB")
    elif args.dither.upper() == "BAYER":
        dithim = gl_d.bayer(image, monos, matrix=args.matrix).convert("RGB")
    else:
        dithim = gl_d.bayer(image, monos, matrix=args.matrix).convert("RGB")

    # Replace colours in image with target palette
    outim = gl_c.replace_colours(dithim, monos, out_palette)

    # Save dithered coloured image
    outim.save(args.outage)

if __name__ == '__main__':
    main()
