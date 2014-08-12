#!/usr/bin/env python

from PIL import Image
from glitches.colour import median_cut
from scipy.cluster.vq import vq
from scipy.spatial import cKDTree
from scipy.weave import inline
from scipy.weave import converters
import numpy as np
import time


# Adapted from
# http://glowingpython.blogspot.co.uk/2012/07/color-quantization.html
def recolour(image, pal):
    palette_array = np.array(pal, dtype=np.uint8)
    im_array = np.reshape(np.array(image), (image.size[0] * image.size[1], 3))
    quant, _ = vq(im_array, palette_array)
    idx = np.reshape(quant, (image.size[1], image.size[0]))
    return Image.fromarray(palette_array[idx])


def recolour2(image, pal):
    tree = cKDTree(np.array(pal, dtype=np.uint8))
    im_array = np.reshape(np.array(image), (image.size[0] * image.size[1], 3))
    for i in xrange(im_array.shape[0]):
            im_array[i] = tree.data[tree.query(im_array[i])[1]]
    im_array = np.reshape(im_array, (image.size[1], image.size[0], 3))
    return Image.fromarray(im_array)


def recolour3(image, pal):
    tree = cKDTree(np.array(pal, dtype=np.uint8))
    im_array = np.reshape(np.array(image), (image.size[0] * image.size[1], 3))
    im_array = tree.data[tree.query(im_array)[1]].astype(np.uint8)
    im_array = np.reshape(im_array, (image.size[1], image.size[0], 3))
    return Image.fromarray(im_array)


def recolour4(image, pal):
    pal_array = np.array(pal, dtype=np.uint8)
    im_array = np.reshape(np.array(image), (image.size[0] * image.size[1], 3))

    nx = im_array.shape[0]  # noqa
    nc = pal_array.shape[0]  # noqa

    code = """
        int n_idx;
        int n_dist, rdist, gdist, bdist, dist;
        for (int i=0; i<nx; ++i)
        {
            n_idx = -1;
            n_dist = -1;

            // Find Nearest Colour
            for (int c=0; c<nc; ++c)
            {
                // Calculate distance
                rdist = im_array(i, 0) - pal_array(c, 0);
                rdist = rdist * rdist;
                gdist = im_array(i, 1) - pal_array(c, 1);
                gdist = gdist * gdist;
                bdist = im_array(i, 2) - pal_array(c, 2);
                bdist = bdist * bdist;
                dist = rdist + gdist + bdist;

                if (n_idx == -1 || dist < n_dist)
                {
                    n_idx = c;
                    n_dist = dist;
                }
            }

            im_array(i,0) = pal_array(n_idx, 0);
            im_array(i,1) = pal_array(n_idx, 1);
            im_array(i,2) = pal_array(n_idx, 2);
        }
        """

    inline(code, ['nx', 'im_array', 'pal_array', 'nc'],
           type_converters=converters.blitz)

    im_array = np.reshape(im_array, (image.size[1], image.size[0], 3))
    return Image.fromarray(im_array)


def main():
    im = Image.open("test.jpg")

    # Extract optimized palette
    palette = median_cut(im, 16)

    # Recolour image
    start_time1 = time.time()
    outim1 = recolour(im, palette)
    outim1.save("test_1.jpg")
    end_time1 = time.time()
    print "Elapsed time %g seconds" % (end_time1 - start_time1)

    # Recolour image
    start_time2 = time.time()
    outim2 = recolour2(im, palette)
    outim2.save("test_2.jpg")
    end_time2 = time.time()
    print "Elapsed time %g seconds" % (end_time2 - start_time2)

    # Recolour image
    start_time3 = time.time()
    outim3 = recolour3(im, palette)
    outim3.save("test_3.jpg")
    end_time3 = time.time()
    print "Elapsed time %g seconds" % (end_time3 - start_time3)

    # Recolour image
    start_time4 = time.time()
    outim4 = recolour4(im, palette)
    outim4.save("test_4.jpg")
    end_time4 = time.time()
    print "Elapsed time %g seconds" % (end_time4 - start_time4)


if __name__ == '__main__':
    main()
