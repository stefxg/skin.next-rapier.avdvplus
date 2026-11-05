#!/usr/bin/env python3
"""Génère l'écran de lecture Tron de Next-Rapier : boutons OSD en disque, barre de progression en trait de lumière.

Usage : python3 _tools/make_tron_osd.py <racine_skin> <dossier_osd_source>
<dossier_osd_source> : copie des boutons Rapier d'origine (les pictogrammes en sont extraits).
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math
CY=(0,216,255); CYL=(150,246,255); WH=(235,252,255)
def extract_icon(path):
    """Renvoie (masque alpha 48x48 du pictogramme, couleurs RGB d'origine)."""
    im=Image.open(path).convert('RGBA'); a=np.asarray(im).astype(float); W,H=im.size
    yy,xx=np.mgrid[0:H,0:W]; r=np.hypot(xx-(W-1)/2,yy-(H-1)/2)
    lum=a[...,:3]@np.array([0.2126,0.7152,0.0722])
    ring=(r>15.5)&(r<18.5)&(a[...,3]>200)
    base=np.median(lum[ring]) if ring.any() else 128
    diff=np.abs(lum-base)
    sat=a[...,:3].max(axis=2)-a[...,:3].min(axis=2)
    m=np.clip((diff-28)/40,0,1)*(r<17.5)*(a[...,3]/255)
    colored=(sat>60)&(m>0.3)
    return m, a[...,:3], colored
def disc(path,focused,S=4,ring=None):
    ring=ring or CY
    W=H=48; m,rgb,colored=extract_icon(path)
    W2=W*S; c=(W2-1)/2
    base=Image.new('RGBA',(W2,W2),(0,0,0,0)); d=ImageDraw.Draw(base)
    R=21.5*S
    d.ellipse([c-R,c-R,c+R,c+R],fill=(4,18,24,235) if focused else (3,8,11,205))
    if focused:  # halo cyan intérieur
        yy,xx=np.mgrid[0:W2,0:W2]; rr=np.hypot(xx-c,yy-c)/R
        hal=np.zeros((W2,W2,4)); hal[...,0],hal[...,1],hal[...,2]=CY; hal[...,3]=np.clip(1-rr,0,1)**1.3*90*(rr<1)
        base.alpha_composite(Image.fromarray(hal.astype(np.uint8),'RGBA'))
    e=Image.new('RGBA',(W2,W2),(0,0,0,0)); ed=ImageDraw.Draw(e)
    ed.ellipse([c-R,c-R,c+R,c+R],outline=(CYL if focused else CY)+(255 if focused else 150,),width=int((2.6 if focused else 1.2)*S))
    R2=18*S; seg=8; gap=10
    for k in range(seg):
        a0=k*360/seg+gap/2-90; a1=(k+1)*360/seg-gap/2-90
        ed.arc([c-R2,c-R2,c+R2,c+R2],a0,a1,fill=tuple(ring)+(235 if focused else (150 if ring!=CY else 80),),width=int((1.6 if focused else 1.1)*S))
    if focused:
        base.alpha_composite(e.filter(ImageFilter.GaussianBlur(1.8*S)))
    base.alpha_composite(e)
    # pictogramme (réduit à 88 % pour laisser respirer l'anneau intérieur)
    icon_rgb=np.zeros((H,W,3)); icon_rgb[:]=WH if focused else (172,198,210)
    icon_rgb[colored]=rgb[colored]
    ic=Image.fromarray(np.dstack([icon_rgb,m*255]).astype(np.uint8),'RGBA').resize((int(W2*0.88),int(W2*0.88)),Image.LANCZOS)
    off=(W2-ic.size[0])//2
    if focused:
        g=Image.new('RGBA',(W2,W2),(0,0,0,0)); gl=Image.new('RGBA',ic.size,CY+(0,)); gl.putalpha(ic.split()[3]); g.alpha_composite(gl,(off,off))
        base.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.5*S)))
    base.alpha_composite(ic,(off,off))
    return base.resize((W,H),Image.LANCZOS)
def bar_track(W=18,H=18,S=4):
    im=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,int(4*S),W*S-1,int(14*S)-1],fill=(4,10,14,200))
    d.line([(0,int(9*S)),(W*S,int(9*S))],fill=CY+(90,),width=int(1*S))
    d.line([(0,int(4*S)),(W*S,int(4*S))],fill=CY+(40,),width=int(0.6*S)); d.line([(0,int(14*S)-1),(W*S,int(14*S)-1)],fill=CY+(40,),width=int(0.6*S))
    return im.resize((W,H),Image.LANCZOS)
def bar_fill(W=18,H=18,bright=True,S=4):
    W2,H2=W*S,H*S; ys=np.linspace(0,H-1,H2)[:,None]; dist=np.abs(ys-8.5)
    glow=np.exp(-(dist/(4.0 if bright else 2.6))**2)
    core=np.clip(1-(dist-(1.4 if bright else 0.9))/0.8,0,1)
    a=np.zeros((H2,W2,4)); col=np.array(CY,float); colc=np.array(WH,float)
    rgb=col*(1-core)[...,None]+colc*core[...,None]
    a[...,:3]=np.broadcast_to(rgb,(H2,W2,3)) if rgb.shape[:2]==(H2,1) else rgb
    alpha=np.maximum(glow*(230 if bright else 110),core*(255 if bright else 130))
    a[...,3]=np.broadcast_to(alpha,(H2,W2))
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8),'RGBA').resize((W,H),Image.LANCZOS)
def bar_head(W=14,H=18,S=4):
    W2,H2=W*S,H*S; yy,xx=np.mgrid[0:H2,0:W2]/S; cx,cy=W-3.5,8.5
    d=np.hypot((xx-cx)/1.0,(yy-cy)/1.0)
    flare=np.exp(-(d/3.6)**2); core=np.exp(-(d/1.6)**2)
    trail=np.exp(-((yy-cy)/1.6)**2)*np.clip((xx)/(cx),0,1)*(xx<=cx)
    alpha=np.clip(np.maximum.reduce([flare*255,trail*220]),0,255)
    a=np.zeros((H2,W2,4)); w=np.clip(core*1.5,0,1)[...,None]
    a[...,:3]=np.array(CY,float)*(1-w)+np.array((255,255,255),float)*w; a[...,3]=alpha
    return Image.fromarray(a.astype(np.uint8),'RGBA').resize((W,H),Image.LANCZOS)


if __name__ == '__main__':
    import os, sys, glob
    root, srcdir = sys.argv[1], sys.argv[2]
    OR = (255, 138, 30)
    osd = os.path.join(root, 'media', 'osd')
    for f in sorted(glob.glob(os.path.join(srcdir, '*.png'))):
        b = os.path.basename(f); foc = b.endswith('-focus.png')
        src = os.path.join(srcdir, b.replace('-focus.png', '-nofocus.png')) if foc else f
        if not os.path.exists(src): src = f
        name = b.replace('osd-', '').replace('-nofocus.png', '').replace('-focus.png', '').replace('.png', '')
        disc(src, foc, ring=OR if name in ('pause', 'stop') else None).save(os.path.join(osd, b), optimize=True)
    c = os.path.join(root, 'media', 'controls')
    bar_track().save(os.path.join(c, 'progress-background.png'), optimize=True)
    bar_fill().save(os.path.join(c, 'scrollbar-slider-horz-focus.png'), optimize=True)
    bar_fill(bright=False).save(os.path.join(c, 'scrollbar-slider-horz-nofocus.png'), optimize=True)
    bar_head().save(os.path.join(c, 'progress-head.png'), optimize=True)
    print('écran de lecture Tron généré')
