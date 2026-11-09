"""Behind the scenes frames: one garage, one kit, every cover (Josh, Nov 8 2026).

  python3 pipeline/bts.py NN --round R [--n 3] [--variants 1,4,6] [--model M]

Each frame = the environment lock (the-first-batch/prompts/bts/environment.md)
           + the track's set block (built from tracks.json, plus prompts/bts/NN-track.md if it exists)
           + one variation below: a slightly different camera angle and slightly different spots for the gear.
References, in order: the track's cover, the environment lock frame, the steel prep table, the TV tray.

Frames rotate through VARIANTS so no two frames in a round share an angle, and the next round
picks up where the last left off. Pin them with --variants. Writes NN.png, NN-prompt.md and
contact-sheet.jpg to work/bts/NN-track/round-R/ and logs spend like gen.py explore.
"""
import argparse, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TFB = os.path.join(ROOT, "the-first-batch")
ENV = os.path.join(TFB, "prompts", "bts", "environment.md")
REFS = [os.path.join(TFB, "assets", "bts", f) for f in ("environment-lock.png", "steel-table.png", "tv-tray.png")]

# Small moves only. Same room, same kit, a few steps and a few degrees apart, like stills from one shoot day.
VARIANTS = [
    ("Camera: the photographer stands about 2 m to the right of where image 2 was taken, near the garage door corner, turned about 30 degrees left, so the set is seen at a clear three quarter angle from its right side and the shelf wall runs along the back of the frame.",
     "Gear: steel prep table in the left foreground with its mess close to the lens, TV tray and tripod in the middle distance at right."),
    ("Camera: low, about knee height, close behind the tripod legs, looking slightly up at the set, so the tripod legs frame the bottom of the picture and the softbox and paper roll read tall against the garage door.",
     "Gear: TV tray just right of the tripod, steel prep table at the far right edge, partly cut off by the frame."),
    ("Camera: from high up, as if standing on a step stool in the back left corner by the shelf wall, looking down at about 35 degrees, so a lot of floor with the taped cord and flour shows.",
     "Gear: the TV tray has been moved to the right of the camera tripod, steel prep table pushed back toward the garage door."),
    ("Camera: from directly beside the stainless steel table on the right, at counter height, looking left across the floured steel top toward the set, the mixer and spray bottle sharp in the near foreground, the set a little soft behind.",
     "Gear: tripod and TV tray in the background at left, set at center left."),
    ("Camera: square to the set from about 4 m back, a wide symmetrical view, the set centered, the camera on its tripod seen from behind in the middle foreground with its rear screen showing the shot.",
     "Gear: TV tray at left of the tripod, steel prep table at right, both a little closer to the set than in image 2."),
    ("Camera: from the left side, against the shelf wall, looking right along the length of the set, so the set is seen side on: the paper sweep curve in profile, the softbox stand in the foreground, the bounce card facing the lens.",
     "Gear: steel prep table behind the set at the far right, TV tray near the camera at left edge."),
]


def track(n):
    d = json.load(open(os.path.join(TFB, "tracks.json")))
    for t in d["tracks"]:
        if t["n"] == n.zfill(2):
            return t
    sys.exit(f"No track {n} in tracks.json")


def cover_ref(t, out_dir):
    """The finished cover, downscaled. Master first, then the 4K render, then the approved source."""
    cands = [t.get("master"), t.get("render_4k"), (t.get("source") or {}).get("repo")]
    for c in cands:
        if c and os.path.exists(os.path.join(ROOT, c)):
            im = Image.open(os.path.join(ROOT, c)).convert("RGB"); im.thumbnail((1600, 1600))
            p = os.path.join(out_dir, "cover-ref.jpg"); im.save(p, quality=90); return p
    sys.exit(f"{t['slug']} has no master, render or source on disk to use as the cover reference")


def set_block(t):
    s = (f"THE SET FOR THIS FRAME (the first reference image is the finished cover it produces, match it exactly):\n"
         f"- On the sweep: {t['device']}. Dough: {t['silhouette']}. The device and dough look exactly like the cover.\n"
         f"- The seamless paper is exactly the backdrop color of image 1 ({t['ground']}, {t['ground_hex']}): match its hue, saturation and depth, not a paler or brighter version.\n")
    extra = os.path.join(TFB, "prompts", "bts", f"{t['slug']}.md")
    if os.path.exists(extra):
        s += open(extra).read().strip() + "\n"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track"); ap.add_argument("--round", required=True); ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--variants", help="comma list of 1 based VARIANTS to use, one per frame")
    ap.add_argument("--model", default=gen.EXPLORE_MODEL); ap.add_argument("--size", default="1K"); ap.add_argument("--aspect", default="3:2")
    a = ap.parse_args()
    t = track(a.track)
    out = os.path.join(ROOT, "work", "bts", t["slug"], f"round-{a.round}"); os.makedirs(out, exist_ok=True)
    refs = [cover_ref(t, out)] + REFS
    head = ("Reference images, in order: 1. the finished cover photograph that this set produces. "
            "2. the environment reference: this exact garage and kit, a frame from the same shoot. "
            "3. the stainless steel prep table. 4. the wooden folding TV tray table.\n\n"
            "Make a candid behind the scenes photograph of how the cover in image 1 was set up for real in the garage from image 2, "
            "with the same kit. Same room, same objects, a different moment of the same shoot day.\n"
            "Image 2 shows what the room and every object look like. Do not copy its camera position or its layout: "
            "the photographer has walked to a new spot and the crew has nudged the gear, as described under THIS FRAME. "
            "The view must clearly differ from image 2.\n\n")
    env = open(ENV).read().split("---", 1)[-1].strip()
    if a.variants:
        picks = [int(v) - 1 for v in a.variants.split(",")]
    else:
        start = (int(a.round) - 1) * a.n if a.round.isdigit() else 0
        picks = [(start + i) % len(VARIANTS) for i in range(a.n)]

    def one(i):
        cam, gear = VARIANTS[picks[i]]
        prompt = f"{head}{env}\n\n{set_block(t)}\nTHIS FRAME (variation {picks[i] + 1}):\n- {cam}\n- {gear}\n"
        open(os.path.join(out, f"{i + 1:02d}-prompt.md"), "w").write(prompt)
        p = os.path.join(out, f"{i + 1:02d}.png")
        gen.save(gen.generate(a.model, prompt, refs, a.aspect, a.size), p)
        gen.log_spend(a.model, a.size, f"bts {t['slug']} round {a.round} frame {i + 1} variation {picks[i] + 1}")
        return p

    with ThreadPoolExecutor(max_workers=3) as ex:
        paths = list(ex.map(one, range(len(picks))))
    gen.contact_sheet(paths, os.path.join(out, "contact-sheet.jpg"))
    print(json.dumps({"out": out, "variations": [p + 1 for p in picks]}))


if __name__ == "__main__":
    main()
