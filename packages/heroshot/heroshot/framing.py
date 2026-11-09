"""Social crops of a square master: 4:5 post and 9:16 story, full height, slid sideways so the
subject's horizontal center sits in the middle. Returns Figma style imageTransform matrices."""
import json, sys
import numpy as np

WIDTHS = {"post_4x5": 0.8, "story_9x16": 0.5625}


def transforms(alpha):
    m = alpha > 0.5
    cols = np.where(m.any(axis=0))[0]
    if cols.size == 0:
        sys.exit("heroshot: empty subject mask")
    n = alpha.shape[1]
    cx = (cols.min() + cols.max() + 1) / 2 / n
    out = {"subject_center_x": round(float(cx), 4), "square": [[1, 0, 0], [0, 1, 0]]}
    for k, w in WIDTHS.items():
        out[k] = [[w, 0, round(float(np.clip(cx - w / 2, 0, 1 - w)), 4)], [0, 1, 0]]
    return out


if __name__ == "__main__":
    print(json.dumps(transforms(np.load(sys.argv[1]))))
