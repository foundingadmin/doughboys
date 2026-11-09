"""Review crops. A 3 x 2 grid of native pixel tiles over a render for a first look at every region,
and contrast boosted seam crops of a finished master around where the render sits on the canvas."""
import os
import numpy as np, cv2
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def grid(render, outdir, tag):
    im = Image.open(render)
    W, H = im.size
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for r in range(2):
        for c in range(3):
            p = os.path.join(outdir, f"{tag}-tile{r * 3 + c + 1}.jpg")
            im.crop((c * W // 3, r * H // 2, (c + 1) * W // 3, (r + 1) * H // 2)).save(p, quality=93)
            paths.append(p)
    return paths


def seams(master, ox, oy, w, h, name):
    """Full view plus four crops at x4 contrast where the render meets the rebuilt backdrop.
    A visible box edge or color step in these is a finish failure."""
    A = np.array(Image.open(master).convert("RGB"))
    S = A.shape[0]
    Image.fromarray(cv2.resize(A, (1000, 1000), interpolation=cv2.INTER_AREA)).save(name + "_full.jpg", quality=88)
    F = A.astype(np.float32)

    def crop(x, y, cw=1400, ch=1000):
        x = int(np.clip(x, 0, S - cw)); y = int(np.clip(y, 0, S - ch))
        c = cv2.resize(F[y:y + ch, x:x + cw], (700, 500), interpolation=cv2.INTER_AREA)
        return np.clip((c - c.mean((0, 1))) * 4 + 128, 0, 255).astype(np.uint8)

    cx, cy = ox + w // 2, oy + h // 2
    g = np.vstack([np.hstack([crop(ox - 700, oy - 500), crop(cx - 700, oy - 500)]),
                   np.hstack([crop(ox - 700, cy - 500), crop(cx + 300, oy + h - 500)])])
    Image.fromarray(g).save(name + "_seams_x4.jpg", quality=85)
    return [name + "_full.jpg", name + "_seams_x4.jpg"]
