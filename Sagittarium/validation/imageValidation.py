#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'thundersoft'

from PIL import Image;


def calc_similar_by_path(lf, rf):
    li, ri = __make_regalur_image(Image.open(lf)), __make_regalur_image(Image.open(rf))
    return __calc_similar(li, ri)

def __make_regalur_image(img, size = (256, 256)):
    return img.resize(size).convert('RGB')

def __calc_similar(li, ri):
    #return hist_similar(li.histogram(), ri.histogram())
    return sum(__hist_similar(l.histogram(), r.histogram()) for l, r in zip(__split_image(li), __split_image(ri))) / 16.0

def __hist_similar(lh, rh):
    assert len(lh) == len(rh)
    return sum(1 - (0 if l == r else float(abs(l - r))/max(l, r)) for l, r in zip(lh, rh))/len(lh)

def __split_image(img, part_size = (64, 64)):
    w, h = img.size
    pw, ph = part_size
    assert w % pw == h % ph == 0
    return [img.crop((i, j, i+pw, j+ph)).copy()
		for i in xrange(0, w, pw)
		for j in xrange(0, h, ph)]