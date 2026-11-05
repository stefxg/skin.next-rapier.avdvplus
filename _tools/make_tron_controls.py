#!/usr/bin/env python3
"""Next-Rapier : contrôles au repos (boutons, séparateurs, barres de défilement, icônes inactives).

Les sources sont relues dans le commit du fork (textures grises de Rapier), donc le script
peut être relancé sans dériver.
Usage : python3 _tools/make_tron_controls.py <racine_skin>
"""
import io, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FORK = '9091c6e'
CY = (0, 216, 255); CYL = (150, 246, 255); WH = (225, 252, 255)
STEEL = (100, 200, 225)   # gris -> acier cyan (inactif)
LINE = (120, 235, 255)    # gris clair -> cyan clair (traits)


def original(root, rel):
    data = subprocess.run(['git', '-C', root, 'show', f'{FORK}:media/{rel}'], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data)).convert('RGBA')


def tint(im, col, sat_max=40, gain=1.0):
    """Remplace les pixels gris par la teinte `col` à luminance égale (alpha conservé)."""
    a = np.asarray(im).astype(float)
    rgb = a[..., :3]; sat = rgb.max(2) - rgb.min(2)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    c = np.array(col, float); clum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    new = np.clip(lum[..., None] / clum * c[None, None, :] * gain, 0, 255)
    m = sat < sat_max
    rgb[m] = new[m]
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def shape(W, H, cut, S=4):
    W2, H2 = W * S, H * S; c = int(cut * S)
    return W2, H2, [(0, 0), (W2 - 1 - c, 0), (W2 - 1, c), (W2 - 1, H2 - 1), (0, H2 - 1)]


def button_nofocus(W=25, H=25, S=4):
    """Bouton au repos : même silhouette que la sélection A+ (coin haut-droit coupé), voile cyan très léger, contour fin."""
    W2, H2, poly = shape(W, H, 3.5, S)
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(poly, fill=(4, 14, 19, 150))
    v = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ImageDraw.Draw(v).polygon(poly, fill=CY + (14,)); im.alpha_composite(v)
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ImageDraw.Draw(e).line(poly + [poly[0]], fill=CY + (135,), width=int(1 * S))
    im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


def scrollbar_background(W=16, H=16, S=4):
    """Rail : fond à peine teinté, contour cyan discret (fonctionne en vertical comme en horizontal)."""
    W2, H2 = W * S, H * S
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W2 - 1, H2 - 1], fill=CY + (12,), outline=CY + (70,), width=int(1 * S))
    return im.resize((W, H), Image.LANCZOS)


def menu_bar_item(W=198, H=38, alt=False, S=4):
    """Onglet de la barre de menu : fond sombre, trait de lumière en bas, petits chanfreins (dans les bords 9 px)."""
    W2, H2 = W * S, H * S; c = int(5 * S)
    poly = [(0, 0), (W2 - 1, 0), (W2 - 1, H2 - 1 - c), (W2 - 1 - c, H2 - 1), (c, H2 - 1), (0, H2 - 1 - c)]
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(poly, fill=(3, 9, 12, 185 if not alt else 210))
    e = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.line([poly[5], poly[4], poly[3], poly[2]], fill=CY + (170 if not alt else 110,), width=int(1.2 * S), joint='curve')
    im.alpha_composite(e.filter(ImageFilter.GaussianBlur(1.5 * S))); im.alpha_composite(e)
    return im.resize((W, H), Image.LANCZOS)


def hline(W, H, row, alpha, col=CY, glow=0):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if glow and row > 0: d.line([(0, row - 1), (W - 1, row - 1)], fill=col + (glow,))
    d.line([(0, row), (W - 1, row)], fill=col + (alpha,))
    return im


STEEL_LIST = [
    'controls/arrow-scroll-left-nofocus.png', 'controls/arrow-scroll-left-nofocus2.png', 'controls/arrow-scroll-up-nofocus.png',
    'controls/arrow-scroll-up-nofocus2.png', 'controls/arrow-scroll-up-nofocus3.png', 'controls/arrow-scroll-up-nofocus4.png',
    'controls/home-nav-arrow-right-nofocus.png', 'controls/nav-arrow-right-nofocus.png', 'controls/nav-arrow-up-nofocus.png',
    'controls/scrollbar-slider-nofocus.png', 'controls/scrollbar-nib-nofocus.png', 'controls/scrollbar-nib-horz-nofocus.png',
    'controls/radio-button-nofocus.png', 'controls/radio-button-nofocus2.png', 'controls/radio-button-nofocus3.png',
    'controls/radio-button-nofocus4.png', 'controls/radio-button-focus2.png', 'controls/dialog-close-nofocus.png',
    'controls/slider-background.png', 'controls/slider-background2.png', 'controls/slider-background3.png',
    'controls/slider-nib-nofocus.png', 'controls/volume-slider-background.png', 'controls/progress-scanning-background.png',
    'controls/settings-toggle-button-nofocus.png', 'controls/settings-toggle-button-nofocus2.png',
    'controls/settings-toggle-button2-nofocus.png', 'controls/settings-toggle-button2-nofocus2.png',
    'views/button-wide-list-nofocus.png',
    'gui/menu-bar-button-arrow-nofocus.png', 'gui/menu-bar-favourites-nofocus.png', 'gui/menu-bar-options-nofocus.png',
    'gui/menu-bar-options-nofocus2.png', 'gui/menu-bar-power-nofocus.png', 'gui/menu-bar-view-options-nofocus.png',
    'gui/breadcrumb-home-nofocus.png',
    'gui/view-3d-wrap.png', 'gui/view-big-icon.png', 'gui/view-extended-list.png', 'gui/view-extended-list2.png', 'gui/view-fanart.png',
    'gui/view-icon.png', 'gui/view-list-info-2.png', 'gui/view-list-info-3.png', 'gui/view-list-info.png', 'gui/view-list.png',
    'gui/view-playlist.png', 'gui/view-thumbnail.png', 'gui/view-thumbs-info.png', 'gui/view-wall.png', 'gui/view-wide-icon.png',
    'gui/view-wrap-info.png',
    'settings/calibrate-bottomright-nofocus.png', 'settings/calibrate-pixelratio-nofocus.png', 'settings/calibrate-reset-nofocus.png',
    'settings/calibrate-subtitles-nofocus.png', 'settings/calibrate-topleft-nofocus.png', 'settings/settings-expand-arrow.png',
]
LINE_LIST = [
    'gui/menu-bar-item-top-border.png', 'gui/menu-bar-item-bottom-border.png', 'gui/menu-bar-separator.png',
    'gui/status-bar-separator.png', 'panels/panel-separator.png', 'gui/bottom-bar-top.png',
    'views/wide-list-header.png', 'views/wrap-list-header.png', 'views/media-info-separator.png',
]

if __name__ == '__main__':
    root = sys.argv[1]; media = os.path.join(root, 'media')
    def save(im, rel): im.save(os.path.join(media, rel), optimize=True)
    save(button_nofocus(), 'controls/button-nofocus.png')
    save(scrollbar_background(), 'controls/scrollbar-background.png')
    save(menu_bar_item(), 'gui/menu-bar-item-nofocus.png')
    save(menu_bar_item(alt=True), 'gui/menu-bar-item-nofocus2.png')
    save(hline(755, 50, 49, 60), 'controls/settings-button-nofocus.png')
    save(hline(150, 3, 2, 55), 'views/list-separator.png')
    save(hline(600, 4, 3, 255, LINE, glow=70), 'views/videoinfo-separator.png')
    DIM = {'controls/radio-button-nofocus.png', 'controls/radio-button-nofocus2.png', 'controls/radio-button-nofocus3.png',
           'controls/radio-button-nofocus4.png'}   # interrupteur « off » : plus sombre que le « on » cyan
    for rel in STEEL_LIST:
        save(tint(original(root, rel), STEEL, gain=0.6 if rel in DIM else 1.0), rel)
    for rel in LINE_LIST:
        save(tint(original(root, rel), LINE), rel)
    print('contrôles Tron générés :', 7 + len(STEEL_LIST) + len(LINE_LIST))
