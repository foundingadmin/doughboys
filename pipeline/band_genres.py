# Fixed genre analysis (Josh, Nov 9 2026): fold the 400 Discogs-EffNet style scores into the band's
# own five genres, Rock, Dance, Funk, Jazz, Jam, then take the top two. Global analysis = raw top styles.
# Counts only each track's top 20 styles (TOP_N): summing all 400 let Rock's 91 styles win every track on noise.
# Usage: python3 pipeline/band_genres.py analysis-full.json labels.json > fixed.json
import json, sys
GEN = ["Rock", "Dance", "Funk", "Jazz", "Jam"]
TOP_N = 20
OVERRIDE = {
    "Jazz---Jazz-Funk": {"Jazz": .5, "Funk": .5},
    "Jazz---Jazz-Rock": {"Jazz": .5, "Rock": .5},
    "Jazz---Afrobeat": {"Funk": 1}, "Funk / Soul---Afrobeat": {"Funk": 1},
    "Rock---Ska": {"Funk": .5, "Jazz": .5}, "Reggae---Ska": {"Funk": .5, "Jazz": .5},
    "Rock---Psychedelic Rock": {"Jam": 1}, "Rock---Prog Rock": {"Jam": 1}, "Rock---Space Rock": {"Jam": 1},
    "Rock---Krautrock": {"Jam": 1}, "Funk / Soul---Psychedelic": {"Jam": .5, "Funk": .5},
    "Funk / Soul---Disco": {"Dance": 1}, "Funk / Soul---Boogie": {"Dance": 1},
}
PARENT = {"Rock": {"Rock": 1}, "Blues": {"Rock": 1}, "Folk, World, & Country": {"Rock": 1}, "Jazz": {"Jazz": 1},
          "Funk / Soul": {"Funk": 1}, "Hip Hop": {"Funk": 1}, "Electronic": {"Dance": 1}, "Latin": {"Dance": 1},
          "Pop": {"Dance": 1}, "Reggae": {"Funk": .5, "Dance": .5}}
def fold(scores, labels, top_n=TOP_N):
    keep = set(sorted(range(len(scores)), key=lambda i: -scores[i])[:top_n]) if top_n else set(range(len(scores)))
    scores = [s if i in keep else 0.0 for i, s in enumerate(scores)]
    t = {g: 0.0 for g in GEN}
    for s, l in zip(scores, labels):
        w = OVERRIDE.get(l) or PARENT.get(l.split("---")[0], {})
        for g, f in w.items(): t[g] += s * f
    tot = sum(t.values()) or 1
    return {g: round(100 * v / tot, 1) for g, v in sorted(t.items(), key=lambda kv: -kv[1])}
if __name__ == "__main__":
    a = json.load(open(sys.argv[1])); labels = json.load(open(sys.argv[2]))["classes"]
    out = {}
    for n, v in a.items():
        f = fold(v["full"], labels); out[n] = {"fixed_share_pct": f, "fixed_top2": list(f)[:2], "global_top": v["genres"][:4]}
    print(json.dumps(out, indent=1))
