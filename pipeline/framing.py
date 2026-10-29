"""Post 4:5 and Canvas 9:16 crops of a square master for the Figma Photo layer.

  python3 pipeline/framing.py MASTER_alpha_small.npy

finish.py saves the device mask next to the master as *_alpha_small.npy. The crops keep the full
height and slide sideways so the device's horizontal center sits in the middle of the board.
Prints the imageTransform matrices to paste into the Figma placement script (docs/figma.md).
"""
import json, sys
import numpy as np

WIDTHS = {"post": 0.8, "canvas": 0.5625}  # 4:5 and 9:16 of a square, full height


def transforms(alpha):
    m = alpha > 0.5
    cols = np.where(m.any(axis=0))[0]
    if cols.size == 0:
        sys.exit("empty device mask")
    n = alpha.shape[1]
    cx = (cols.min() + cols.max() + 1) / 2 / n
    out = {"device_center_x": round(float(cx), 4), "cover": [[1, 0, 0], [0, 1, 0]]}
    for k, w in WIDTHS.items():
        tx = float(np.clip(cx - w / 2, 0, 1 - w))
        out[k] = [[w, 0, round(tx, 4)], [0, 1, 0]]
    return out


if __name__ == "__main__":
    print(json.dumps(transforms(np.load(sys.argv[1]))))
