#!/usr/bin/env python

from PIL import Image
import math
from operator import itemgetter
from scipy.cluster.vq import vq
import numpy as np


class Box(object):
    def __init__(self, colours=None):
        # Setup colours
        if colours is None:
            self.colours = []
            self._r0 = 0
            self._r1 = 255
            self._g0 = 0
            self._g1 = 255
            self._b0 = 0
            self._b1 = 255
        else:
            self.colours = colours
            self.resize()

    @property
    def rsize(self):
        return self._r1 - self._r0

    @property
    def gsize(self):
        return self._g1 - self._g0

    @property
    def bsize(self):
        return self._b1 - self._b0

    @property
    def size(self):
        return (self.rsize, self.gsize, self.bsize)

    @property
    def avg(self):
        n = len(self.colours)
        r = int(math.floor(sum(col[0] for col in self.colours) / n))
        g = int(math.floor(sum(col[1] for col in self.colours) / n))
        b = int(math.floor(sum(col[2] for col in self.colours) / n))
        return r, g, b

    def resize(self):
        self._r0 = min(col[0] for col in self.colours)
        self._r1 = max(col[0] for col in self.colours)
        self._g0 = min(col[1] for col in self.colours)
        self._g1 = max(col[1] for col in self.colours)
        self._b0 = min(col[2] for col in self.colours)
        self._b1 = max(col[2] for col in self.colours)

    def split(self, axis):
        # Sort colours by axis
        self.colours = sorted(self.colours, key=itemgetter(axis))

        # Find median
        med_idx = len(self.colours) / 2

        # Create splits
        return Box(self.colours[:med_idx]), Box(self.colours[med_idx:])


def get_colours(image):
    colours = image.getcolors(image.size[0] * image.size[1])
    return [c[1] for c in colours]


def median_cut(image, num_colours):
    colours = get_colours(image)

    # Create initial box
    boxes = [Box(colours)]

    # Find longest dimension/box
    while len(boxes) < num_colours:
        longest_box = -1
        longest_dim = -1
        longest_size = -1
        for b in range(len(boxes)):
            size = boxes[b].size
            for d in range(3):
                if size[d] > longest_size:
                    longest_box = b
                    longest_dim = d
                    longest_size = size[d]

        # Split longest dimension/box
        split_box = boxes[longest_box]
        a, b = split_box.split(longest_dim)

        # Replace split box
        boxes = boxes[:longest_box] + [a, b] + boxes[longest_box+1:]

    # Average colours
    colours = [x.avg for x in boxes]

    return colours


# Adapted from
# http://glowingpython.blogspot.co.uk/2012/07/color-quantization.html
def recolour(image, pal):
    palette_array = np.array(pal, dtype=np.uint8)
    im_array = np.reshape(np.array(image), (image.size[0] * image.size[1], 3))
    quant, _ = vq(im_array, palette_array)
    idx = np.reshape(quant, (image.size[1], image.size[0]))
    return Image.fromarray(palette_array[idx])
