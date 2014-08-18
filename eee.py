#!/usr/bin/env python

import glitches.dithering as gl_d
import glitches.colour as gl_c
from PIL import Image
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


def resize(image, w, h, bgcolor="black"):
    ow, oh = image.size
    if w == -1 and h == -1:
        return image
    elif w == -1 and h != -1:
        w = ow * (float(h) / float(oh))
        w = int(w)
        return image.resize((w, h))
    elif w != -1 and h == -1:
        h = oh * (float(w) / float(ow))
        h = int(h)
        return image.resize((w, h))
    else:
        # Fit longest axis
        if ow <= oh:
            nh = h
            nw = (float(nh) / float(oh)) * ow
            nw = int(nw)
            im2 = image.resize((nw, nh))
            wdiff = int((w - nw) / 2.0)
            im = Image.new("RGB", (w, h), bgcolor)
            im.paste(im2, (wdiff, 0))
        else:
            nw = w
            nh = (float(nw) / float(ow)) * oh
            nh = int(nh)
            im2 = image.resize((nw, nh))
            hdiff = int((h - nh) / 2.0)
            im = Image.new("RGB", (w, h), bgcolor)
            im.paste(im2, (0, hdiff))
        return im


def main():
    parser = ArgumentParser()
    parser.add_argument("inage", metavar='INPUT', type=str)
    parser.add_argument("outage", metavar='OUTPUT', type=str)
    parser.add_argument("-p", "--palette", type=str, default="AUTO")
    parser.add_argument("-d", "--dither", type=str, default="BAYER")
    parser.add_argument("-iw", "--width", type=int, default=-1)
    parser.add_argument("-ih", "--height", type=int, default=-1)
    args = parser.parse_args()

    image = Image.open(args.inage)

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
    image = resize(image, args.width, args.height)
    
    # Prequantize
    image = gl_c.quantize(image, gl_c.mono_palette(num_colours * 4))

    # Create monochrome palette for quantization
    monos = gl_c.mono_palette(num_colours)

    # Dither image based on monochrome palette
    if args.dither.upper() == "FS":
        dithim = gl_d.floyd_steinberg(image, monos, mode="MONO").convert("RGB")
    elif args.dither.upper() == "BAYER":
        dithim = gl_d.bayer(image, monos, matrix=2).convert("RGB")
    else:
        dithim = gl_d.bayer(image, monos, matrix=2).convert("RGB")

    # Replace colours in image with target palette
    outim = gl_c.replace_colours(dithim, monos, out_palette)

    # Save dithered coloured image
    outim.save(args.outage)

if __name__ == '__main__':
    main()
