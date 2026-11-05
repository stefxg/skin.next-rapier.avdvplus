#!/usr/bin/env python3
"""Next-Rapier : texture de l'impulsion lumineuse qui court sur le haut des fenêtres (gui/frame-pulse.png).

600 x 16, border="33,0,40,0" : marge transparente à gauche (chanfrein du cadre), traînée étirée au centre,
tête lumineuse non étirée à droite. L'include NextFramePulse l'anime en zoom horizontal depuis x = 33.
Usage : python3 _tools/make_tron_pulse.py <racine_skin>
"""
import os, sys
import numpy as np
from PIL import Image
CY = np.array((0, 216, 255), float); WH = np.array((255, 255, 255), float)
W, H, S = 600, 16, 4
L, HEAD0, HEAD1 = 33, 560, 590
xs = (np.arange(W * S) + 0.5) / S; ys = (np.arange(H * S) + 0.5) / S
X, Y = np.meshgrid(xs, ys); dy = np.abs(Y - 8)
tail_t = np.clip((X - L) / (HEAD0 - L), 0, 1) * (X >= L) * (X < HEAD1 - 4)
tail = (tail_t ** 1.5) * (np.exp(-(dy / 2.4) ** 2) * 0.5 + np.exp(-(dy / 0.75) ** 2) * 0.6)
hx = 580.0
dh = np.hypot((X - hx) / 5.5, dy / 2.0)
head = np.exp(-dh ** 2) + 0.85 * np.exp(-(np.hypot((X - hx) / 15, dy / 5.0)) ** 2)
head *= (X < HEAD1)
alpha = np.clip(np.maximum(tail * 255, head * 255), 0, 255)
core = np.clip(np.maximum(np.exp(-dh ** 2) * 1.4, (tail_t ** 2) * np.exp(-(dy / 0.6) ** 2) * 0.8), 0, 1)[..., None]
rgb = CY * (1 - core) + WH * core
im = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), 'RGBA').resize((W, H), Image.LANCZOS)
im.save(os.path.join(sys.argv[1], 'media', 'gui', 'frame-pulse.png'), optimize=True)
print('impulsion générée')
