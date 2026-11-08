# doughboys

Titus musical endeavors. Home of the production pipeline for **The First Batch** by Chillsbury Doughboys: device photos generated with Gemini, finished into 6704 square masters, placed into the Figma covers.

## Start a Claude Code session

1. **Environment.** Use the custom cloud environment with `GEMINI_API_KEY`. In its network settings, allow `generativelanguage.googleapis.com`, `mcp.figma.com` and `www.figma.com` on top of the defaults, or give it full network access.
2. **Repo.** Pick `foundingadmin/doughboys`.
3. **Figma.** Make sure the Figma connector is on for the session. Claude checks it in the smoke test and says so if it is missing.
4. **Drive.** One time: deploy the Drive drop web app and add `TFB_DRIVE_URL` and `TFB_DRIVE_KEY` to the environment, see `the-first-batch/docs/drive.md`. Without it everything works except the automatic upload to Drive.
5. **First message.** Paste this:

```
Read CLAUDE.md, run the session smoke test, then build a track cover.
```

After that, talk to it per track: "build a track cover", "Spice, run the 4K", "Determinator, explore round 2", "keep going". The playbook is `.claude/skills/build-track-cover/SKILL.md`.

## What is here

| Path | What |
|---|---|
| `CLAUDE.md` | Operating manual Claude Code reads every session |
| `.claude/skills/build-track-cover/` | The per track playbook any session follows |
| `pipeline/cover.py` | One command per step, keeps tracks.json current |
| `pipeline/drive.py`, `pipeline/drive_drop.gs` | Upload renders and masters to Drive |
| `pipeline/gen.py` | Gemini explore, tight crop, 4K render |
| `pipeline/finish.py` | 4K render to 6704 square master with the backdrop matched to the track swatch |
| `pipeline/check.py` | Review crops and color comparison |
| `pipeline/framing.py` | Post and Canvas crops for the Figma boards |
| `the-first-batch/tracks.json` | State of all nine tracks, Figma and Drive ids |
| `the-first-batch/prompts/` | Approved 4K prompts and the explore series lock |
| `the-first-batch/assets/` | Approved sources, renders, masters, textures, brand |
| `the-first-batch/docs/` | Art direction, Figma recipe, lessons |
| `the-first-batch/review/` | Check crops and Figma board screenshots for Josh |

Design lives in Figma: https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee
