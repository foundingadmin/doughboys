"""Project config and item state, one file: heroshot.json at the repo root.

Every write goes through Project.edit(), which takes a file lock and re-reads the file first,
so two steps running at once never drop each other's records.
"""
import contextlib, datetime, fcntl, json, os, sys
from zoneinfo import ZoneInfo

CONFIG_NAME = "heroshot.json"

DEFAULTS = {
    "project": "Untitled series",
    "dir": "art",
    "timezone": "UTC",
    "approver": "the creative director",
    "budget_usd_month": 30,
    "models": {"explore": "gemini-3.1-flash-image-preview", "render": "gemini-3-pro-image-preview"},
    "explore": {"n": 3, "size": "1K", "aspect": "1:1"},
    "render": {"size": "4K"},
    "finish": {"canvas": 6704, "falloff": 0.75, "horizon": 0.16, "template": None},
    "prices_usd": {"flash 1K": 0.067, "flash 2K": 0.067, "flash 4K": 0.15, "pro 1K": 0.134, "pro 2K": 0.134, "pro 4K": 0.24},
    "figma": {"file_key": "", "review_page_id": "", "sections": {}},
    "drive": {"default_folder": ""},
    "items": [],
}


def die(msg):
    sys.exit(f"heroshot: {msg}")


def find_root(start=None):
    d = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.exists(os.path.join(d, CONFIG_NAME)):
            return d
        up = os.path.dirname(d)
        if up == d:
            die(f"no {CONFIG_NAME} here or above. Run `heroshot init` in the repo first.")
        d = up


def merged(cfg):
    out = json.loads(json.dumps(DEFAULTS))
    for k, v in cfg.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


class Project:
    def __init__(self, root=None):
        self.root = root or find_root()
        self.path = os.path.join(self.root, CONFIG_NAME)
        self.cfg = self._read()

    def _read(self):
        return merged(json.load(open(self.path)))

    # paths
    @property
    def art(self):
        return os.path.join(self.root, self.cfg["dir"])

    def p(self, *parts, make=False):
        path = os.path.join(self.art, *parts)
        if make:
            os.makedirs(path, exist_ok=True)
        return path

    def work(self, *parts):
        path = os.path.join(self.root, "work", *parts)
        os.makedirs(path, exist_ok=True)
        return path

    def rel(self, path):
        return os.path.relpath(path, self.root)

    # time, in the project's own timezone (cloud containers run on UTC)
    @property
    def tz(self):
        return ZoneInfo(self.cfg.get("timezone") or "UTC")

    def now(self):
        return datetime.datetime.now(self.tz)

    def today(self):
        return self.now().date().isoformat()

    # items
    def item(self, item_id, cfg=None):
        cfg = cfg or self.cfg
        key = str(item_id)
        for t in cfg["items"]:
            if t["id"] == key or t["id"] == key.zfill(len(t["id"])) or t.get("slug") == key:
                return t
        die(f"no item {item_id} in {CONFIG_NAME}. `heroshot status` lists them, `heroshot add` adds one.")

    @contextlib.contextmanager
    def edit(self):
        """Lock, re-read, yield the live config, write it back."""
        with open(os.path.join(self.root, ".heroshot.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            raw = json.load(open(self.path))
            yield raw
            raw["updated"] = self.today()
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, self.path)
            self.cfg = merged(raw)
