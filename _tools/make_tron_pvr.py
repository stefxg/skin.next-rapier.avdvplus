#!/usr/bin/env python3
"""Next-Rapier : guide TV (cases de l'EPG en coins coupés à filet lumineux, icônes PVR).

Les cases restent blanches : leur couleur vient du colordiffuse des XML (couleur de genre, LiveTVColumnColor…).
Usage : python3 _tools/make_tron_pvr.py <racine_skin>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from make_tron_controls import original, tint, LINE, STEEL
from make_tron_icons import neon_icon

S = 4


def P(v): return int(round(v * S))


def cell(left=True, right=True, fill=150, W=64, H=64, cut=6, inset=1):
    W2, H2 = W * S, H * S; o = P(inset); c = P(cut)
    x0 = o if left else -P(4); x1 = W2 - 1 - o if right else W2 + P(4); y0, y1 = o, H2 - 1 - o
    poly = [(x0 + (c if left else 0), y0), (x1, y0), (x1, y1 - (c if right else 0)), (x1 - (c if right else 0), y1), (x0, y1), (x0, y0 + (c if left else 0))]
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(poly, fill=(255, 255, 255, fill))
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.line(poly + [poly[0]], fill=(255, 255, 255, 255), width=P(1.3), joint='curve')
    im.alpha_composite(e.filter(ImageFilter.GaussianBlur(P(1.2)))); im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    root = sys.argv[1]; pvr = os.path.join(root, 'media', 'pvr')
    def save(im, name): im.save(os.path.join(pvr, name), optimize=True)
    save(cell(), 'column.png')
    save(cell(right=False), 'column-left.png')
    save(cell(left=False), 'column-right.png')
    save(cell(fill=205), 'column-focus.png')
    for n in ('add', 'edit', 'remove'):
        save(tint(original(root, f'pvr/button_Inline-{n}.png'), STEEL), f'button_Inline-{n}.png')
        save(tint(original(root, f'pvr/button_Inline-{n}-focus.png'), LINE), f'button_Inline-{n}-focus.png')
    for n in ('conflict', 'enabled', 'error', 'none', 'recording', 'timer'):
        save(tint(original(root, f'pvr/status_{n}.png'), LINE), f'status_{n}.png')
    for n in ('DefaultPVR.png', 'DefaultPVRLogo.png'):
        save(neon_icon(original(root, 'pvr/' + n)), n)
    print('guide TV Tron généré')
