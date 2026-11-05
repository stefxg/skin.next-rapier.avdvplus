#!/usr/bin/env python3
"""Next-Rapier : menu contextuel (haut / milieu / bas) et en-tête des menus de l'OSD, en cadre B+.

Les trois morceaux sont découpés dans un même dessin pour que les bords tombent juste.
Bords dans les XML : haut 40,30,40,0 (aussi retourné en bas), milieu 40,2,40,2, bas 40,0,40,30,
en-tête OSD 40,50,40,0. Les motifs restent dans les 40 px de chaque côté.
Usage : python3 _tools/make_tron_menu.py <racine_skin>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

CY = (0, 216, 255); CYL = (150, 246, 255); WH = (225, 252, 255)
S = 4; W = 715; M = 8          # M = marge d'ombre / de halo autour du cadre


def P(v): return int(round(v * S))


def frame(H, header_line=None, top=True, bottom=True):
    """Dessine le cadre complet (W x H) ; les morceaux sont ensuite découpés."""
    W2, H2 = W * S, H * S
    x0, y0, x1, y1 = P(M), P(M), P(W - 1 - M), P(H - 1 - M); c = P(14)
    if not top: y0 = -P(40)
    if not bottom: y1 = H2 + P(40)
    poly = [(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)]
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(poly, fill=(3, 8, 11, 242))
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    thin, thick = P(1.2), P(3)
    ed.line(poly + [poly[0]], fill=CY + (200,), width=thin, joint='curve')
    if top:
        ed.line([(x0, y0 + c + P(12)), (x0, y0 + c), (x0 + c, y0), (x0 + c + P(14), y0)], fill=WH + (255,), width=thick, joint='curve')
        b = P(12); ed.line([(x1 - b, y0), (x1, y0), (x1, y0 + b)], fill=WH + (255,), width=thick, joint='curve')
        for k in range(3):   # pastilles dans l'angle haut-droit
            xx = x1 - P(30) + k * P(5); ed.rectangle([xx, y0 + P(4), xx + P(2.5), y0 + P(6.5)], fill=CYL + (255,))
    if bottom:
        ed.line([(x1, y1 - c - P(12)), (x1, y1 - c), (x1 - c, y1), (x1 - c - P(14), y1)], fill=WH + (255,), width=thick, joint='curve')
        b = P(12); ed.line([(x0, y1 - b), (x0, y1), (x0 + b, y1)], fill=WH + (255,), width=thick, joint='curve')
        xx = x0 + P(5)
        for wdt in (7, 5, 3):   # barres de données dans l'angle bas-gauche
            ed.rectangle([xx, y1 - P(6), xx + P(wdt), y1 - P(3.5)], fill=CY + (230,)); xx += P(wdt + 2.5)
    if header_line is not None:   # filet sous le titre (en-tête OSD)
        yy = P(header_line); ed.line([(x0 + P(6), yy), (x1 - P(6), yy)], fill=CY + (90,), width=P(1))
    im.alpha_composite(e.filter(ImageFilter.GaussianBlur(P(2.2))))
    im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    root = sys.argv[1]; gui = os.path.join(root, 'media', 'gui')
    full = frame(32 + 40 + 30)
    full.crop((0, 0, W, 32)).save(os.path.join(gui, 'context-menu-top.png'), optimize=True)
    full.crop((0, 32 + 19, W, 32 + 21)).save(os.path.join(gui, 'context-menu-middle.png'), optimize=True)
    full.crop((0, 72, W, 102)).save(os.path.join(gui, 'context-menu-bottom.png'), optimize=True)
    frame(50 + 40, header_line=44, bottom=False).crop((0, 0, W, 50)).save(os.path.join(gui, 'dialog-background3-top.png'), optimize=True)
    print('menu contextuel Tron généré')
