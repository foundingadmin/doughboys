"""Backdrop falloff template for finish.py, measured from an approved master (Deluge v1).

  python3 pipeline/backdrop_template.py the-first-batch/assets/photos/01-deluge/01-deluge-final-v1.jpg

Writes pipeline/backdrop_template.npz: lightness and hue of the backdrop relative to its glow, on a
128 square grid in canvas fractions, device masked out and filled. finish.py colors it to each track's
swatch so every cover's backdrop falls off the way Deluge v1 does.
"""
import sys, os
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finish import device_mask, push_pull, ELLIPSE, wrap

Image.MAX_IMAGE_PIXELS = None
GRID = 128

src = sys.argv[1]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backdrop_template.npz')
im = Image.open(src).convert('RGB')
n = 838
rgb = np.array(im.resize((n, n), Image.BOX))
alpha = device_mask(np.array(im.resize((1676, 1676), Image.BOX)))
a = cv2.resize(alpha, (n, n), interpolation=cv2.INTER_AREA)
known = (cv2.dilate((a > 0.02).astype(np.uint8), np.ones((9, 9))) == 0).astype(np.float32)
lab = cv2.cvtColor(rgb.astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
lab = np.where(known[..., None] > 0, lab, push_pull(lab, known))
lab = cv2.GaussianBlur(lab, (0, 0), n * 0.01)
gy, gx = np.mgrid[0:n, 0:n] / n
cx, cy, rx, ry = ELLIPSE
ell = (((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1) & (known > 0)
L = lab[..., 0]; h = np.arctan2(lab[..., 2], lab[..., 1]); C = np.hypot(lab[..., 1], lab[..., 2])
Lg = float(np.median(L[ell])); hg = float(np.median(h[ell])); Cg = float(np.median(C[ell]))
dL = cv2.resize(L - Lg, (GRID, GRID), interpolation=cv2.INTER_AREA)
dh = cv2.resize(wrap(h - hg), (GRID, GRID), interpolation=cv2.INTER_AREA)
np.savez(out, dL=dL.astype(np.float32), dh=dh.astype(np.float32), source=os.path.basename(src), glow_LCh=np.array([Lg, Cg, hg], np.float32))
print(f'{out}  glow L {Lg:.1f} C {Cg:.1f}  dL corners {dL[0,0]:.1f} {dL[0,-1]:.1f} {dL[-1,0]:.1f} {dL[-1,-1]:.1f}  dh range {np.degrees(dh.min()):.1f} {np.degrees(dh.max()):.1f}')
