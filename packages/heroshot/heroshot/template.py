"""Measure a backdrop falloff template from an approved master, so every later finish falls off the
same way and the series reads as a set. Lightness relative to the glow, 128 square grid, subject masked."""
import os
import numpy as np, cv2
from PIL import Image
from .finish import device_mask, push_pull, ELLIPSE

Image.MAX_IMAGE_PIXELS = None
GRID = 128


def measure(src, out):
    im = Image.open(src).convert("RGB")
    n = 838
    rgb = np.array(im.resize((n, n), Image.BOX))
    alpha = device_mask(np.array(im.resize((n * 2, n * 2), Image.BOX)))
    a = cv2.resize(alpha, (n, n), interpolation=cv2.INTER_AREA)
    known = (cv2.dilate((a > 0.02).astype(np.uint8), np.ones((9, 9))) == 0).astype(np.float32)
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
    lab = np.where(known[..., None] > 0, lab, push_pull(lab, known))
    lab = cv2.GaussianBlur(lab, (0, 0), n * 0.01)
    gy, gx = np.mgrid[0:n, 0:n] / n
    cx, cy, rx, ry = ELLIPSE
    ell = (((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1) & (known > 0)
    L = lab[..., 0]
    Lg = float(np.median(L[ell]))
    dL = cv2.resize(L - Lg, (GRID, GRID), interpolation=cv2.INTER_AREA).astype(np.float32)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    np.savez(out, dL=dL, source=os.path.basename(src))
    return {"template": out, "glow_L": round(Lg, 1),
            "corners_dL": [round(float(v), 1) for v in (dL[0, 0], dL[0, -1], dL[-1, 0], dL[-1, -1])]}
