#!/usr/bin/env python3
"""Génère les textures de sélection Tron (style A+) de Next-Rapier.

Usage : python3 _tools/make_tron_focus.py <racine_skin>
Attention : les bascules des réglages recopient leur indicateur 1/2 depuis la texture en place.
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
CY=(0,216,255); WH=(225,252,255)
def focus(W,H,b,style='A',S=4):
    """style A : voile cyan dégradé + contour fin + barre lumineuse à gauche + coin coupé.
       style B : pas de contour ; barre gauche + soulignement lumineux + voile très léger."""
    W2,H2=W*S,H*S; im=Image.new('RGBA',(W2,H2),(0,0,0,0)); d=ImageDraw.Draw(im)
    # voile : dégradé horizontal (fort à gauche) — dans la zone centrale étirée
    a=np.zeros((H2,W2,4)); xs=np.linspace(0,1,W2)
    alpha=(70-45*xs) if style=='A' else (42-34*xs)
    a[...,0],a[...,1],a[...,2]=CY; a[...,3]=alpha[None,:]
    veil=Image.fromarray(a.astype(np.uint8),'RGBA')
    m=Image.new('L',(W2,H2),0); md=ImageDraw.Draw(m)
    cut=int(3*S)
    poly=[(0,0),(W2-1-cut,0),(W2-1,cut),(W2-1,H2-1),(0,H2-1)]
    md.polygon(poly,fill=255); im.paste(veil,(0,0),m)
    e=Image.new('RGBA',(W2,H2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    if style=='A':
        ed.line(poly+[poly[0]],fill=CY+(230,),width=int(1*S))
    else:
        ed.line([(0,H2-1-int(0.5*S)),(W2-1,H2-1-int(0.5*S))],fill=CY+(240,),width=int(1.4*S))
        ed.line([(W2-1-cut,0),(W2-1,cut)],fill=CY+(200,),width=int(1*S))
    ed.rectangle([0,int(1*S),int(3*S),H2-1-int(1*S)],fill=WH+(255,))      # barre gauche (3 px, dans la marge fixe)
    glow=e.filter(ImageFilter.GaussianBlur(1.6*S))
    im.alpha_composite(glow); im.alpha_composite(e)
    return im.resize((W,H),Image.LANCZOS)

def focus_plus(W,H,b,S=4):
    """A+ : voile cyan plus dense, contour lumineux avec halo, barre gauche 4 px très lumineuse, coin coupé."""
    W2,H2=W*S,H*S; im=Image.new('RGBA',(W2,H2),(0,0,0,0))
    a=np.zeros((H2,W2,4)); xs=np.linspace(0,1,W2); ys=np.linspace(0,1,H2)
    alpha=(115-60*xs)[None,:]*(1.0-0.25*ys[:,None])
    a[...,0],a[...,1],a[...,2]=CY; a[...,3]=alpha
    veil=Image.fromarray(a.astype(np.uint8),'RGBA')
    cut=int(3.5*S)
    poly=[(0,0),(W2-1-cut,0),(W2-1,cut),(W2-1,H2-1),(0,H2-1)]
    m=Image.new('L',(W2,H2),0); ImageDraw.Draw(m).polygon(poly,fill=255); im.paste(veil,(0,0),m)
    e=Image.new('RGBA',(W2,H2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    ed.line(poly+[poly[0]],fill=(120,240,255,255),width=int(1.2*S))
    ed.rectangle([0,0,int(4*S),H2-1],fill=WH+(255,))
    im.alpha_composite(e.filter(ImageFilter.GaussianBlur(2.2*S))); im.alpha_composite(e.filter(ImageFilter.GaussianBlur(0.8*S))); im.alpha_composite(e)
    return im.resize((W,H),Image.LANCZOS)


def focus_alt(W, H, S=4):
    W2, H2 = W * S, H * S; im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    a = np.zeros((H2, W2, 4)); xs = np.linspace(0, 1, W2); a[..., 0], a[..., 1], a[..., 2] = CY; a[..., 3] = (40 - 22 * xs)[None, :]
    cut = int(3.5 * S); poly = [(0, 0), (W2 - 1 - cut, 0), (W2 - 1, cut), (W2 - 1, H2 - 1), (0, H2 - 1)]
    m = Image.new('L', (W2, H2), 0); ImageDraw.Draw(m).polygon(poly, fill=255); im.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'), (0, 0), m)
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.line(poly + [poly[0]], fill=CY + (110,), width=int(1 * S)); ed.rectangle([0, 0, int(3 * S), H2 - 1], fill=CY + (170,))
    im.alpha_composite(e); return im.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    import os, sys
    media = os.path.join(sys.argv[1], 'media')
    for p in ['views/list-focus.png', 'gui/menu-bar-button-focus.png', 'controls/button-focus.png', 'controls/settings-button-focus.png',
              'settings/settings-cat-button-alt-focus.png', 'gui/home-submenu-item-focus.png', 'views/wide-list-focus.png']:
        f = os.path.join(media, p); focus_plus(*Image.open(f).size, 5).save(f, optimize=True)
    for p in ['views/list-alt-focus.png', 'controls/button-alt-focus.png']:
        f = os.path.join(media, p); focus_alt(*Image.open(f).size).save(f, optimize=True)
    for p in ['controls/settings-toggle-button-focus.png', 'controls/settings-toggle-button-focus2.png',
              'controls/settings-toggle-button2-focus.png', 'controls/settings-toggle-button2-focus2.png']:
        f = os.path.join(media, p); old = Image.open(f).convert('RGBA'); W, H = old.size
        a = np.asarray(old).astype(int); sat = a[..., :3].max(axis=2) - a[..., :3].min(axis=2)
        pill = (sat < 40) & (a[..., 3] > 200); pill[:, :W - 120] = False
        ys, xs = np.where(pill); box = (xs.min() - 1, ys.min() - 1, xs.max() + 2, ys.max() + 2)
        new = focus_plus(W, H, 5); new.alpha_composite(old.crop(box), (box[0], box[1])); new.save(f, optimize=True)
    print('sélections Tron générées')
