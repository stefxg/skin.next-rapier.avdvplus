#!/usr/bin/env python3
"""Next-Rapier : pastilles vu / non vu / en cours en disque, icônes par défaut en néon.

Usage : python3 _tools/make_tron_icons.py <racine_skin>
Sources relues dans le commit du fork (voir make_tron_controls.original).
"""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from make_tron_controls import original, tint, LINE

CY = (0, 216, 255); CYL = (150, 246, 255); WH = (235, 252, 255)
ICON = (120, 225, 250)
S = 4


def disc(progress=None, watched=False, W=40):
    """progress : None (non vu), 0..1 (en cours : segments allumés), watched : coche."""
    W2 = W * S; c = (W2 - 1) / 2
    im = Image.new('RGBA', (W2, W2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    R = 17.6 * S; R2 = 11.8 * S
    d.ellipse([c - R, c - R, c + R, c + R], fill=(3, 10, 14, 215))
    if watched:   # cœur lumineux
        yy, xx = np.mgrid[0:W2, 0:W2]; rr = np.hypot(xx - c, yy - c) / R
        h = np.zeros((W2, W2, 4)); h[..., 0], h[..., 1], h[..., 2] = CY; h[..., 3] = np.clip(1 - rr, 0, 1) ** 1.2 * 120 * (rr < 1)
        im.alpha_composite(Image.fromarray(h.astype(np.uint8), 'RGBA'))
    e = Image.new('RGBA', (W2, W2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.ellipse([c - R, c - R, c + R, c + R], outline=(CYL if watched else CY) + (255 if watched else 225,), width=int(2.4 * S))
    seg, gap = 8, 14
    lit = 0 if progress is None else progress * 360
    for k in range(seg):
        a0 = k * 360 / seg + gap / 2 - 90; a1 = (k + 1) * 360 / seg - gap / 2 - 90
        ed.arc([c - R2, c - R2, c + R2, c + R2], a0, a1, fill=CY + (85,), width=int(2.2 * S))
    if progress:   # progression : arc continu allumé depuis midi
        ed.arc([c - R2, c - R2, c + R2, c + R2], -90, -90 + lit, fill=WH + (255,), width=int(3.6 * S))
    if watched:
        p = [(c - 7.5 * S, c + 0.5 * S), (c - 2.2 * S, c + 6 * S), (c + 8 * S, c - 6 * S)]
        ed.line(p, fill=WH + (255,), width=int(3.6 * S), joint='curve')
    im.alpha_composite(e.filter(ImageFilter.GaussianBlur(1.6 * S)))
    im.alpha_composite(e)
    return im.resize((W, W), Image.LANCZOS)


def neon_icon(im, glow=0.55):
    t = tint(im, ICON)
    W, H = t.size; r = max(1.5, W * 0.022)
    a = t.split()[3].filter(ImageFilter.GaussianBlur(r))
    g = Image.new('RGBA', (W, H), CY + (0,)); g.putalpha(a.point(lambda v: int(v * glow)))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(t)
    return out


if __name__ == '__main__':
    root = sys.argv[1]; media = os.path.join(root, 'media')
    def save(im, rel): im.save(os.path.join(media, rel), optimize=True)
    for rel in ('OverlayClean.png', 'OverlayCleanAlt.png'): save(disc(), rel)
    for rel in ('OverlayWatched.png', 'OverlayWatchedWhite.png'): save(disc(watched=True), rel)
    for p in range(10, 100, 10):
        for suf in ('', '-alt'): save(disc(progress=p / 100), f'watched/watched-{p}pct{suf}.png')
    for n in ('HD', 'SD', '4K', '8K', 'Unknown'):
        save(tint(original(root, f'Overlay{n}.png'), LINE), f'Overlay{n}.png')
    for n in ('RAR', 'ZIP', 'Spoiler', 'Trained', 'HasTrainer'):
        rel = f'Overlay{n}.png'
        if os.path.exists(os.path.join(media, rel)): save(tint(original(root, rel), LINE), rel)
    icons = sorted(os.path.basename(p) for p in glob.glob(os.path.join(media, 'Default*.png')))
    icons += ['notification.png', 'notification2.png', 'settings.png', 'download.png']
    for rel in icons: save(neon_icon(original(root, rel)), rel)
    save(tint(original(root, 'pointer.png'), LINE), 'pointer.png')
    print('pastilles et icônes Tron générées :', 2 + 2 + 18 + len(icons) + 1)
