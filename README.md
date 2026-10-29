# doughboys

Titus musical endeavors. Home of the production pipeline for **The First Batch** by Chillsbury Doughboys: device photos generated with Gemini, finished into 6704 square masters, placed into the Figma covers.

## Start a Claude Code session

1. **Environment.** Use the custom cloud environment with `GEMINI_API_KEY`. In its network settings, allow `generativelanguage.googleapis.com`, `mcp.figma.com` and `www.figma.com` on top of the defaults, or give it full network access.
2. **Repo.** Pick `foundingadmin/doughboys`.
3. **Figma.** Make sure the Figma connector is on for the session. Claude checks it in the smoke test and says so if it is missing.
4. **First message.** Paste this:

```
Read CLAUDE.md, run the session smoke test, then place Deluge v1 in Figma as the wiring test. After that, Traycee: tight crop 4K re-run from the 81:2 source.
```

After that, talk to it per track: "Spice, run the 4K", "Determinator, explore a new round", "Boombap, start".

## What is here

| Path | What |
|---|---|
| `CLAUDE.md` | Operating manual Claude Code reads every session |
| `pipeline/gen.py` | Gemini explore, tight crop, 4K render |
| `pipeline/finish.py` | 4K render to 6704 square master with the backdrop matched to the track swatch |
| `pipeline/check.py` | Review crops and color comparison |
| `pipeline/framing.py` | Post and Canvas crops for the Figma boards |
| `the-first-batch/tracks.json` | State of all nine tracks, Figma and Drive ids |
| `the-first-batch/prompts/` | Approved 4K prompts and the explore series lock |
| `the-first-batch/assets/` | Approved sources, renders, masters, textures, brand |
| `the-first-batch/docs/` | Art direction, Figma recipe, lessons |

Design lives in Figma: https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee
