#!/usr/bin/env python3
"""Next-Rapier : étuis d'affiches (sélection néon A+ / repos) et panneaux des fiches et des vues.

Usage : python3 _tools/make_tron_covers.py <racine_skin>
Les lignes restent dans la zone non étirée du 9-slice (border de chaque usage dans les XML).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from make_tron_controls import original, tint, LINE

CY = (0, 216, 255); CYL = (150, 246, 255); WH = (225, 252, 255); EDGE = (120, 240, 255)
S = 4


def P(v): return int(round(v * S))


def poly_tr(x0, y0, x1, y1, c):
    """Rectangle au coin haut-droit coupé (silhouette de la sélection A+)."""
    return [(x0, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1), (x0, y1)]


def poly_b(x0, y0, x1, y1, c):
    """Rectangle aux coins haut-gauche et bas-droit coupés (silhouette des cadres B+)."""
    return [(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)]


def mask(size, poly):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).polygon(poly, fill=255); return m


def case(W, H, at, lw, cut, focus):
    """Étui d'affiche. `at` = position de la ligne depuis le bord (unités texture)."""
    W2, H2 = W * S, H * S
    o = P(at + lw / 2)
    poly = poly_tr(o, o, W2 - 1 - o, H2 - 1 - o, P(cut))
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    m = mask((W2, H2), poly)
    im.paste((3, 9, 12, 225 if focus else 205), (0, 0), m)
    if focus:
        veil = Image.new('RGBA', (W2, H2), CY + (78,)); im.paste(Image.alpha_composite(im, veil), (0, 0), m)
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    if focus:
        ed.line(poly + [poly[0]], fill=EDGE + (255,), width=P(lw), joint='curve')
        if at >= 1.5:   # halo : deux passes pour un vrai néon
            halo = e.filter(ImageFilter.GaussianBlur(P(min(at, 3) * 0.8))); im.alpha_composite(halo); im.alpha_composite(halo)
        im.alpha_composite(e.filter(ImageFilter.GaussianBlur(P(0.6))))
        core = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
        ImageDraw.Draw(core).line(poly + [poly[0]], fill=WH + (255,), width=max(1, P(lw * 0.45)), joint='curve')
        im.alpha_composite(e); im.alpha_composite(core)
    else:
        ed.line(poly + [poly[0]], fill=CY + (95,), width=P(lw), joint='curve')
        im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


def panel_box(W, H, fill, line, cut, inset=0.5, lw=1.0, brackets=False, shape='b'):
    W2, H2 = W * S, H * S; o = P(inset)
    poly = (poly_b if shape == 'b' else poly_tr)(o, o, W2 - 1 - o, H2 - 1 - o, P(cut))
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    im.paste(fill, (0, 0), mask((W2, H2), poly))
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.line(poly + [poly[0]], fill=line, width=P(lw), joint='curve')
    if brackets:   # chanfreins lumineux + équerres, comme panel.png (B+)
        x0, y0, x1, y1, c = o, o, W2 - 1 - o, H2 - 1 - o, P(cut); bt = P(2)
        ed.line([(x0, y0 + c + P(1)), (x0, y0 + c), (x0 + c, y0), (x0 + c + P(1), y0)], fill=WH + (255,), width=bt)
        ed.line([(x1, y1 - c - P(1)), (x1, y1 - c), (x1 - c, y1), (x1 - c - P(1), y1)], fill=WH + (255,), width=bt)
        ed.line([(x1 - P(5), y0), (x1, y0), (x1, y0 + P(5))], fill=CYL + (255,), width=bt)
        ed.line([(x0, y1 - P(5)), (x0, y1), (x0 + P(5), y1)], fill=CYL + (255,), width=bt)
        im.alpha_composite(e.filter(ImageFilter.GaussianBlur(P(1))))
    im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


FOCUS = {   # chemin : (W, H, at, lw, cut)
    'covers/cover-case-focus.png': (37, 37, 2.2, 2.2, 4), 'covers/cover-case-focus2.png': (37, 37, 2.2, 2.2, 4),
    'covers/cover-case-curved-focus.png': (37, 37, 2.2, 2.2, 4), 'covers/cover-case-noshadow-focus.png': (27, 27, 0.2, 1.6, 3),
    'covers/cover-case-thumbnail-focus.png': (202, 293, 3.5, 2, 8), 'covers/cover-case-thumbnail2-focus.png': (293, 293, 3.5, 2, 8),
    'covers/cover-case-curved-big-focus.png': (244, 330, 3, 2, 7), 'covers/item-focus-background2.png': (127, 127, 3, 2, 7),
}
NOFOCUS = {
    'covers/cover-case-nofocus.png': (37, 37, 2.5, 1, 4), 'covers/cover-case-curved-nofocus.png': (37, 37, 2.5, 1, 4),
    'covers/cover-case-noshadow-nofocus.png': (27, 27, 0.2, 1, 3), 'covers/cover-case-thumbnail-nofocus.png': (202, 293, 3.5, 1.2, 8),
    'covers/cover-case-thumbnail2-nofocus.png': (293, 293, 3.5, 1.2, 8), 'covers/item-focus-background.png': (127, 127, 3, 1.2, 7),
}

if __name__ == '__main__':
    root = sys.argv[1]; media = os.path.join(root, 'media')
    def save(im, rel): im.save(os.path.join(media, rel), optimize=True)
    for rel, (W, H, at, lw, cut) in FOCUS.items(): save(case(W, H, at, lw, cut, True), rel)
    for rel, (W, H, at, lw, cut) in NOFOCUS.items(): save(case(W, H, at, lw, cut, False), rel)
    # étui sombre derrière les affiches des listes et fiches (border 4, bordersize 4) : opaque + filet cyan
    c2 = panel_box(126, 166, (5, 10, 13, 255), CY + (110,), 3, inset=0.5, lw=1, shape='tr'); save(c2, 'covers/cover-case2.png')
    save(panel_box(25, 25, (2, 7, 10, 255), CY + (95,), 3, inset=0.5), 'panels/panel3.png')                  # bandeaux d'infos (affichés à 60 %)
    save(panel_box(25, 25, CYL + (170,), CYL + (255,), 3.5, inset=0.5), 'panels/panel-content-border2.png')  # voile des vues (affiché à 9 %)
    save(panel_box(25, 25, CY + (14,), CY + (120,), 3.5, inset=0.5), 'panels/panel-content-border.png')
    save(panel_box(32, 32, CY + (38,), CY + (150,), 4, inset=0.5, shape='tr'), 'views/genre-background.png')
    save(panel_box(610, 267, (3, 8, 11, 215), CY + (150,), 5.5, inset=1, brackets=True), 'panels/content-panel.png')
    save(tint(original(root, 'panels/notify-panel.png'), LINE), 'panels/notify-panel.png')
    print('étuis et panneaux Tron générés')
