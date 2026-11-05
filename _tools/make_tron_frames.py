#!/usr/bin/env python3
"""Génère les cadres Tron de Next-Rapier (dialogues B+ et panneau).

Usage : python3 _tools/make_tron_frames.py <racine_skin>
"""
from PIL import Image, ImageDraw, ImageFilter
CY=(0,216,255); CYL=(150,246,255); WH=(225,252,255)
S=3  # supersampling
def P(v): return int(round(v*S))
def finish(base, edge, glow):
    W,H=base.size
    if glow: base.alpha_composite(edge.filter(ImageFilter.GaussianBlur(glow*S)))
    base.alpha_composite(edge)
    return base.resize((W//S,H//S),Image.LANCZOS)
def dialog(W,H,ins,variant):
    W2,H2=W*S,H*S; x0,y0,x1,y1=P(ins[0]),P(ins[1]),P(W-1-ins[2]),P(H-1-ins[3]); c=P(26)
    base=Image.new('RGBA',(W2,H2),(0,0,0,0)); d=ImageDraw.Draw(base)
    poly=[(x0+c,y0),(x1,y0),(x1,y1-c),(x1-c,y1),(x0,y1),(x0,y0+c)]
    d.polygon(poly,fill=(3,8,11,242))
    sl=Image.new('RGBA',(W2,H2),(0,0,0,0)); sd=ImageDraw.Draw(sl)
    for y in range(y0+P(4),y1,P(5)): sd.line([(x0,y),(x1,y)],fill=CY+(8,),width=S)
    m=Image.new('L',(W2,H2),0); ImageDraw.Draw(m).polygon(poly,fill=255); base.paste(Image.alpha_composite(base,sl),(0,0),m)
    e=Image.new('RGBA',(W2,H2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    ed.line(poly+[poly[0]],fill=CY+(200,),width=P(1.2),joint='curve')     # outer thin line
    if variant>=1:
        # double line on the top-left: thick bright segment along the cut, then along the top
        t=P(3.2)
        ed.line([(x0,y0+c+P(40)),(x0,y0+c),(x0+c,y0),(x0+c+P(150),y0)],fill=WH+(255,),width=t,joint='curve')
        # inner circuit trace: from left edge inset, 45° step, ending with a node
        i=P(9)
        # piste verticale le long du bord gauche (ne croise pas le titre) : 45° vers l'intérieur puis nœud
        tr=[(x0+i,y0+c+P(4)),(x0+i,y0+c+P(70)),(x0+i+P(10),y0+c+P(80)),(x0+i+P(10),y0+c+P(150))]
        ed.line(tr,fill=CY+(200,),width=P(1.4),joint='curve')
        r=P(3.2); nx,ny=tr[-1]; ed.ellipse([nx-r,ny-r,nx+r,ny+r],outline=CYL+(255,),width=P(1.4))
        # bottom-right: mirrored thick segment + trace + node
        ed.line([(x1,y1-c-P(40)),(x1,y1-c),(x1-c,y1),(x1-c-P(150),y1)],fill=WH+(255,),width=t,joint='curve')
        tr2=[(x1-i,y1-c-P(4)),(x1-i,y1-c-P(70)),(x1-i-P(10),y1-c-P(80)),(x1-i-P(10),y1-c-P(150))]
        ed.line(tr2,fill=CY+(200,),width=P(1.4),joint='curve'); nx,ny=tr2[-1]; ed.ellipse([nx-r,ny-r,nx+r,ny+r],outline=CYL+(255,),width=P(1.4))
        # corner brackets top-right & bottom-left
        b=P(22); bt=P(3)
        ed.line([(x1-b,y0-P(0)),(x1,y0),(x1,y0+b)],fill=WH+(255,),width=bt,joint='curve')
        ed.line([(x0,y1-b),(x0,y1),(x0+b,y1)],fill=WH+(255,),width=bt,joint='curve')
    if variant>=2:
        # pips on right edge (in the top-right corner zone) and a segmented line on top
        for k in range(3):
            yy=y0+P(30)+k*P(9); ed.rectangle([x1-P(7),yy,x1-P(3),yy+P(5)],fill=CYL+(255,))
        for k in range(6):
            xx=x1-P(60)-k*P(10); ed.rectangle([xx,y0+P(4),xx+P(6),y0+P(6)],fill=CY+(220,))
    return finish(base,e,3)
def panel(W,H,variant):
    W2,H2=W*S,H*S; x0,y0,x1,y1=P(1),P(1),P(W-2),P(H-2); c=P(6.5)
    base=Image.new('RGBA',(W2,H2),(0,0,0,0)); d=ImageDraw.Draw(base)
    poly=[(x0+c,y0),(x1,y0),(x1,y1-c),(x1-c,y1),(x0,y1),(x0,y0+c)]
    d.polygon(poly,fill=(3,8,11,205))
    e=Image.new('RGBA',(W2,H2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    ed.line(poly+[poly[0]],fill=CY+(175,),width=P(1),joint='curve')
    if variant>=1:
        bt=P(2.2)
        ed.line([(x0,y0+c+P(1)),(x0,y0+c),(x0+c,y0),(x0+c+P(1),y0)],fill=WH+(255,),width=bt)   # bright cut TL
        ed.line([(x1,y1-c-P(1)),(x1,y1-c),(x1-c,y1),(x1-c-P(1),y1)],fill=WH+(255,),width=bt)   # bright cut BR
        ed.line([(x1-P(6),y0),(x1,y0),(x1,y0+P(6))],fill=CYL+(255,),width=bt)                   # bracket TR
        ed.line([(x0,y1-P(6)),(x0,y1),(x0+P(6),y1)],fill=CYL+(255,),width=bt)                   # bracket BL
    return finish(base,e,1.2 if variant else 0)

from PIL import ImageFont
import os, sys
MICRO=os.path.join(sys.argv[1] if len(sys.argv)>1 else '.', 'fonts', 'BrunoAceSC-Regular.ttf')
def dialog_v3(W,H,ins,corner):
    """corner = (l,t,r,b) zones non étirées du 9-slice : les motifs fins y restent."""
    W2,H2=W*S,H*S; x0,y0,x1,y1=P(ins[0]),P(ins[1]),P(W-1-ins[2]),P(H-1-ins[3]); c=P(24)
    L,T,R,B=[P(v) for v in corner]
    base=Image.new('RGBA',(W2,H2),(0,0,0,0)); d=ImageDraw.Draw(base)
    poly=[(x0+c,y0),(x1,y0),(x1,y1-c),(x1-c,y1),(x0,y1),(x0,y0+c)]
    d.polygon(poly,fill=(3,8,11,244))
    # scanlines + léger dégradé de lumière en haut
    sl=Image.new('RGBA',(W2,H2),(0,0,0,0)); sd=ImageDraw.Draw(sl)
    for y in range(y0+P(4),y1,P(5)): sd.line([(x0,y),(x1,y)],fill=CY+(8,),width=S)
    for k in range(P(40)): sd.line([(x0,y0+k),(x1,y0+k)],fill=CY+(int(16*(1-k/P(40))),),width=1)
    m=Image.new('L',(W2,H2),0); ImageDraw.Draw(m).polygon(poly,fill=255); base.paste(Image.alpha_composite(base,sl),(0,0),m)
    e=Image.new('RGBA',(W2,H2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    thin=P(1.2); thick=P(3.2); mid=P(1.6)
    ed.line(poly+[poly[0]],fill=CY+(190,),width=thin,joint='curve')
    # --- haut-gauche : double chanfrein (épais blanc + fin cyan décalé), trait plein puis pointillé sur le haut
    ed.line([(x0,y0+c+P(34)),(x0,y0+c),(x0+c,y0),(x0+c+P(120),y0)],fill=WH+(255,),width=thick,joint='curve')
    o=P(6); ed.line([(x0+o,y0+c+P(14)),(x0+o,y0+c+o*0.4),(x0+c+o*0.4,y0+o),(x0+c+P(30),y0+o)],fill=CY+(230,),width=thin,joint='curve')
    for k in range(5):
        xx=x0+c+P(132)+k*P(9); ed.line([(xx,y0),(xx+P(4),y0)],fill=WH+(230,),width=thick)
    # --- bord gauche : deux pistes parallèles à 45° + nœuds
    i=P(10)
    ed.line([(x0+i,y0+c+P(26)),(x0+i,y0+c+P(80)),(x0+i+P(9),y0+c+P(89)),(x0+i+P(9),y0+c+P(150))],fill=CY+(210,),width=mid,joint='curve')
    ed.line([(x0+i+P(5),y0+c+P(26)),(x0+i+P(5),y0+c+P(60))],fill=CY+(120,),width=thin)
    r=P(3); nx,ny=x0+i+P(9),y0+c+P(150); ed.ellipse([nx-r,ny-r,nx+r,ny+r],outline=CYL+(255,),width=mid)
    # --- haut-droit (zone d'angle) : équerre, arc de disque, règle graduée, pastilles, micro-texte
    b=P(18); ed.line([(x1-b,y0),(x1,y0),(x1,y0+b)],fill=WH+(255,),width=thick,joint='curve')
    cx,cy=x1-P(17),y0+P(17); rr=P(10)
    ed.arc([cx-rr,cy-rr,cx+rr,cy+rr],start=180,end=450,fill=CY+(220,),width=mid)
    ed.arc([cx-rr+P(4),cy-rr+P(4),cx+rr-P(4),cy+rr-P(4)],start=200,end=330,fill=CYL+(255,),width=thin)
    for k in range(6):  # règle graduée descendant le long du bord droit, dans la zone d'angle
        yy=y0+P(32)+k*P(4); ed.line([(x1-P(4 if k%3 else 8),yy),(x1,yy)],fill=CY+(200,),width=thin)
    for k in range(3):
        xx=x1-P(38)+k*P(6); ed.rectangle([xx,y0+P(4),xx+P(3),y0+P(7)],fill=CYL+(255,))
    # --- bas-gauche : équerre + barres de données segmentées (zone d'angle)
    ed.line([(x0,y1-b),(x0,y1),(x0+b,y1)],fill=WH+(255,),width=thick,joint='curve')
    xx=x0+P(6)
    for wdt in (10,7,5,3,2):
        ed.rectangle([xx,y1-P(9),xx+P(wdt),y1-P(5)],fill=CY+(220,)); xx+=P(wdt+3)
    # micro-texte dans l'angle bas-gauche, au-dessus des barres
    f=ImageFont.truetype(MICRO,P(6.5)); ed.text((x0+P(6),y1-P(22)),'N-R 07',font=f,fill=CY+(170,))
    # --- bas-droit : double chanfrein + piste qui remonte + hachures
    ed.line([(x1,y1-c-P(34)),(x1,y1-c),(x1-c,y1),(x1-c-P(120),y1)],fill=WH+(255,),width=thick,joint='curve')
    ed.line([(x1-o,y1-c-P(14)),(x1-o,y1-c-o*0.4),(x1-c-o*0.4,y1-o),(x1-c-P(30),y1-o)],fill=CY+(230,),width=thin,joint='curve')
    for k in range(5):
        xx=x1-c-P(136)-k*P(9); ed.line([(xx,y1),(xx+P(4),y1)],fill=WH+(230,),width=thick)
    ed.line([(x1-i,y1-c-P(26)),(x1-i,y1-c-P(80)),(x1-i-P(9),y1-c-P(89)),(x1-i-P(9),y1-c-P(150))],fill=CY+(210,),width=mid,joint='curve')
    nx,ny=x1-i-P(9),y1-c-P(150); ed.ellipse([nx-r,ny-r,nx+r,ny+r],outline=CYL+(255,),width=mid)
    for k in range(4):   # hachures diagonales près du chanfrein bas-droit
        hx=x1-P(30)+k*P(4); ed.line([(hx,y1-P(4)),(hx+P(4),y1-P(10))],fill=CY+(170,),width=thin)
    return finish(base,e,3)


if __name__ == '__main__':
    root = sys.argv[1]
    specs = {'dialog-background.png': ((9, 12, 9, 12), (50, 70, 50, 75)), 'dialog-background2.png': ((9, 12, 9, 12), (50, 50, 50, 75)),
             'dialog-background3.png': ((9, 12, 9, 12), (50, 50, 50, 50)), 'dialog-background4.png': ((9, 9, 9, 9), (50, 50, 50, 50))}
    for f, (ins, cor) in specs.items():
        dialog_v3(715, 442, ins, cor).save(os.path.join(root, 'media', 'panels', f), optimize=True)
    panel(31, 31, 2).save(os.path.join(root, 'media', 'panels', 'panel.png'), optimize=True)
    print('cadres Tron générés')
