from PIL import Image


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
