#!/usr/bin/env python3
"""Passe les bleus de Rapier en cyan Tron: Legacy (textures PNG/JPG + couleurs ARGB des XML).

Usage : python3 _tools/recolor_cyan.py <racine_skin> [--dry-run]

Seuls les pixels / couleurs dont la teinte est bleue (200-250°) et saturée sont modifiés :
teinte ramenée vers 186-199° (cyan), saturation +5 %, luminosité +15 %.
Textures « *focus* » (fonds de sélection sous texte blanc) : luminance d'origine conservée (+15 %).
Le résultat (teinte < 200°) n'est plus concerné : le script est idempotent.
Exclus : media/flagging (logos codecs/HDR), media/studios, fonts, extras, resources.
"""
import os, re, sys
import numpy as np
from PIL import Image

H_MIN, H_MAX, S_MIN = 200.0, 250.0, 0.15
EXCLUDE_DIRS = ('media/flagging', 'media/studios')


def shift_hsv(h, s, v):
    """h en degrés, s et v entre 0 et 1 (tableaux numpy)."""
    m = (h >= H_MIN) & (h <= H_MAX) & (s >= S_MIN)
    h2 = np.where(m, 186.0 + (h - H_MIN) * 0.25, h)
    s2 = np.where(m, np.minimum(1.0, s * 1.05), s)
    v2 = np.where(m, np.minimum(1.0, v * 1.15), v)
    return h2, s2, v2, m


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.max(rgb, axis=-1); mn = np.min(rgb, axis=-1); d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-9
    rm = nz & (mx == r); gm = nz & (mx == g) & ~rm; bm = nz & ~rm & ~gm
    h[rm] = (60 * ((g[rm] - b[rm]) / d[rm]) + 360) % 360
    h[gm] = 60 * ((b[gm] - r[gm]) / d[gm]) + 120
    h[bm] = 60 * ((r[bm] - g[bm]) / d[bm]) + 240
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    c = v * s; hp = (h / 60.0) % 6; x = c * (1 - np.abs(hp % 2 - 1)); z = np.zeros_like(h)
    conds = [(hp < 1), (hp >= 1) & (hp < 2), (hp >= 2) & (hp < 3), (hp >= 3) & (hp < 4), (hp >= 4) & (hp < 5), (hp >= 5)]
    vals = [(c, x, z), (x, c, z), (z, c, x), (z, x, c), (x, z, c), (c, z, x)]
    r = np.select(conds, [a for a, _, _ in vals]); g = np.select(conds, [b for _, b, _ in vals]); b = np.select(conds, [cc for _, _, cc in vals])
    m = v - c
    return np.stack([r + m, g + m, b + m], axis=-1)


def luminance(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def recolor_image(path, dry):
    im = Image.open(path)
    mode = im.mode
    rgba = np.asarray(im.convert('RGBA')).astype(np.float64) / 255.0
    h, s, v = rgb_to_hsv(rgba[..., :3])
    h2, s2, v2, m = shift_hsv(h, s, v)
    if not m.any():
        return False
    rgb2 = hsv_to_rgb(h2, s2, v2)
    if 'focus' in os.path.basename(path).lower():
        # fonds de sélection : on garde la luminance du bleu d'origine (+15 %) pour que
        # le texte blanc posé dessus reste aussi lisible qu'avec Rapier
        l0 = luminance(rgba[..., :3]) * 1.15; l1 = luminance(rgb2)
        k = np.where(l1 > 1e-6, np.minimum(1.0, l0 / np.maximum(l1, 1e-6)), 1.0)
        rgb2 = np.clip(rgb2 * k[..., None], 0, 1)
    out = rgba.copy(); out[..., :3] = np.where(m[..., None], rgb2, rgba[..., :3])
    if not dry:
        res = Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8), 'RGBA')
        if path.lower().endswith('.jpg') or mode == 'RGB':
            res = res.convert('RGB')
        elif mode in ('LA', 'L', 'P'):
            res = res if mode == 'P' and False else res
        res.save(path, optimize=True) if path.lower().endswith('.png') else res.save(path, quality=92)
    return True


COLOR_RE = re.compile(r'(?<![0-9A-Fa-f])([0-9A-Fa-f]{2})([0-9A-Fa-f]{6})(?![0-9A-Fa-f])')


def recolor_hex(aa, rrggbb):
    rgb = np.array([[int(rrggbb[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]])
    h, s, v = rgb_to_hsv(rgb)
    h2, s2, v2, m = shift_hsv(h, s, v)
    if not m.any():
        return None
    r, g, b = (hsv_to_rgb(h2, s2, v2)[0] * 255 + 0.5).astype(int)
    lower = rrggbb.islower() or aa.islower()
    out = f'{aa}{r:02X}{g:02X}{b:02X}'
    return out.lower() if lower else out


def recolor_xml(path, dry):
    txt = open(path, encoding='utf-8').read()
    changes = []
    def rep(mo):
        # seulement dans des contextes de couleur : valeur d'élément ou d'attribut
        new = recolor_hex(mo.group(1), mo.group(2))
        if new is None:
            return mo.group(0)
        changes.append((mo.group(0), new))
        return new
    pattern = re.compile(r'(?<=[>"\[ =,])([0-9A-Fa-f]{2})([0-9A-Fa-f]{6})(?=[<"\] ,])')
    new_txt = pattern.sub(rep, txt)
    if changes and not dry:
        open(path, 'w', encoding='utf-8').write(new_txt)
    return changes


def main():
    root = os.path.abspath(sys.argv[1]); dry = '--dry-run' in sys.argv
    n_img = 0
    for dp, dn, fn in os.walk(os.path.join(root, 'media')):
        rel = os.path.relpath(dp, root).replace(os.sep, '/')
        if rel.startswith(EXCLUDE_DIRS):
            continue
        for f in fn:
            if f.lower().endswith(('.png', '.jpg')):
                if recolor_image(os.path.join(dp, f), dry):
                    n_img += 1
    n_xml = 0; total = 0
    for sub in ('720p', 'colors'):
        for dp, dn, fn in os.walk(os.path.join(root, sub)):
            for f in fn:
                if f.endswith('.xml'):
                    if sub == 'colors' and f != 'defaults.xml':
                        continue  # thèmes de couleur orange / rouge / flat : inchangés
                    ch = recolor_xml(os.path.join(dp, f), dry)
                    if ch:
                        n_xml += 1; total += len(ch)
                        for a, b in sorted(set(ch)):
                            print(f'  {f}: {a} -> {b}')
    print(f'{"[simulation] " if dry else ""}images recolorées : {n_img} ; fichiers XML : {n_xml} ({total} couleurs)')


if __name__ == '__main__':
    main()
