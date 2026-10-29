"""Compare a finished master to a reference (optional) and render review crops.
usage: python3 check.py OUT.jpg [REF.jpg] --ox 824 --oy 1656 --w 5056 --h 3392 --name tag"""
import argparse, numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('ref', nargs='?')
ap.add_argument('--ox', type=int); ap.add_argument('--oy', type=int); ap.add_argument('--w', type=int); ap.add_argument('--h', type=int)
ap.add_argument('--name', default='check')
a = ap.parse_args()
A = np.array(Image.open(a.out).convert('RGB'))
S = A.shape[0]
if a.ref:
    V = np.array(Image.open(a.ref).convert('RGB'))
    s = 16; n = S // s
    As = cv2.resize(A, (n, n), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    Vs = cv2.resize(V, (n, n), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    al = cv2.resize(np.load(a.out.rsplit('.', 1)[0] + '_alpha_small.npy'), (n, n), interpolation=cv2.INTER_AREA)
    bg = cv2.dilate((al > 0.02).astype('uint8'), np.ones((9, 9))) == 0
    la, lv = cv2.cvtColor(As, cv2.COLOR_RGB2LAB), cv2.cvtColor(Vs, cv2.COLOR_RGB2LAB)
    dE = np.linalg.norm(la - lv, axis=-1)
    inside = np.zeros((n, n), bool); inside[a.oy // s:(a.oy + a.h) // s, a.ox // s:(a.ox + a.w) // s] = True
    print('BG dE inside render: median %.1f p90 %.1f' % (np.median(dE[bg & inside]), np.percentile(dE[bg & inside], 90)))
    print('BG dE margins: median %.1f p90 %.1f' % (np.median(dE[bg & ~inside]), np.percentile(dE[bg & ~inside], 90)))
    pa = cv2.resize(A, (900, 900), interpolation=cv2.INTER_AREA); pv = cv2.resize(V, (900, 900), interpolation=cv2.INTER_AREA)
    Image.fromarray(np.concatenate([pv, np.full((900, 20, 3), 255, np.uint8), pa], 1)).save(a.name + '_side.jpg', quality=88)
else:
    Image.fromarray(cv2.resize(A, (1000, 1000), interpolation=cv2.INTER_AREA)).save(a.name + '_full.jpg', quality=88)
# seam crops, contrast x4
F = A.astype(np.float32)
def crop(x, y, w=1400, h=1000):
    x = int(np.clip(x, 0, S - w)); y = int(np.clip(y, 0, S - h))
    c = cv2.resize(F[y:y + h, x:x + w], (700, 500), interpolation=cv2.INTER_AREA)
    return np.clip((c - c.mean((0, 1))) * 4 + 128, 0, 255).astype(np.uint8)
cx, cy = a.ox + a.w // 2, a.oy + a.h // 2
g = np.vstack([np.hstack([crop(a.ox - 700, a.oy - 500), crop(cx - 700, a.oy - 500)]),
               np.hstack([crop(a.ox - 700, cy - 500), crop(cx + 300, a.oy + a.h - 500)])])
Image.fromarray(g).save(a.name + '_seams_x4.jpg', quality=85)
