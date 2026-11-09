# heroshot

An AI product photography pipeline built to be driven by Claude Code. Low res explore frames in, finished square masters out, with an approver signing off at four gates and every paid call logged against a monthly budget.

It came out of a nine cover album series and carries what that taught: crop tight before the 4K pass, name every label in the hi res prompt, rebuild the backdrop instead of keeping the generator's, keep one hue edge to edge, and never spend on 4K without a fresh written yes.

## What it does

| Step | Command | Gate |
|---|---|---|
| Set up a repo | `heroshot init` | |
| Smoke test | `heroshot doctor` | |
| Add an item | `heroshot add 01 --title "Night Owl" --subject "1985 clock radio" --hex "#DE9F65"` | |
| Draft an explore prompt | `heroshot prompt 01 --round 1` | |
| Explore, 3 frames at 1K on the fast model | `heroshot explore 01 --round 1` | 1 · approver picks a frame |
| Lock the pick | `heroshot lock 01 work/01-night-owl/round-1/02.png --pick R1-2` | |
| Write the hi res prompt | `art/prompts/hires/01-night-owl.md` | 2 · approver okays the prompt |
| Tight crop and 4K render | `heroshot render 01 --approved "go, 4K it"` | |
| Check crops, review board | built by Claude in Figma | 3 · approver picks the render |
| Finish: rebuild the backdrop in the swatch | `heroshot finish 01 --render art/assets/01-night-owl/...-a.jpg` | 4 · approver passes the master |
| Save to Drive | `heroshot drive 01` | |
| Lock the series falloff from a loved master | `heroshot template art/assets/01-night-owl/01-night-owl-final-v1.jpg` | |
| Month spend vs budget | `heroshot spend` | |

`explore` and `render` take `--dry-run` to print the prompt and cost without spending, and stop before crossing `budget_usd_month` unless you pass `--over-budget`.

## Install into a project

```bash
pip install "git+https://github.com/OWNER/heroshot.git"
```

```bash
heroshot init --name "Project name" --approver "Sam" --tz America/New_York
```

`init` writes into the repo:

- `heroshot.json` · config (models, budget, finish defaults, Figma and Drive ids) and every item's state
- `art/prompts/explore/series-lock.md` · the explore template every prompt is built from. Lock its style line with the approver first
- `art/prompts/hires/_example.md` · the shape of a 4K "keep this exact photograph" prompt
- `art/docs/brief.md`, `art/docs/lessons.md` · the living brief and the lessons log, seeded with what earlier projects learned
- `.claude/skills/heroshot/` · the playbook Claude follows, plus Figma and Drive references, a review board script and the Drive upload web app
- a heroshot section in `CLAUDE.md`, and `work/` in `.gitignore`

Re-running `init` keeps your config and edited templates and refreshes the skill, so a package upgrade reaches the playbook.

For a cloud environment, add the install to its setup script so every session starts with it:

```bash
pip install "git+https://github.com/OWNER/heroshot.git"
```

## Environment

- `GEMINI_API_KEY` · required. Explore runs on Nano Banana 2 Flash, 4K on Nano Banana Pro (ids in `heroshot.json` `models`, `heroshot models` lists what your key reaches)
- `HEROSHOT_DRIVE_URL`, `HEROSHOT_DRIVE_KEY` · optional, for Drive upload (`.claude/skills/heroshot/reference/drive.md`)
- Network: `generativelanguage.googleapis.com`, plus `mcp.figma.com` and `www.figma.com` for Figma uploads
- Keys live only in the environment, never in a file or commit

`rembg` downloads its segmentation weights on first use. The finish step runs on CPU in a few minutes and wants about 5 GB of memory per job.

## The finish, in one paragraph

The generator's backdrop is never kept. `finish` isolates the subject, builds a square canvas (6704 by default) whose backdrop is one smooth gradation of the item's swatch shaped by a falloff template, adds a faint cyclorama horizon behind the subject, keeps only the render's own contact shadows and film grain, and places the render 1:1 in the center with its edge pixels cleaned of the old color. It reports how close the glow lands to the swatch (deltaE under 3 is a match), the hue spread (near 0), how deep the corners fall, and whether the subject touches the crop edge. The default template is a neutral studio sweep. Once the approver loves one master, `heroshot template` measures it and every later finish falls off the same way.

## Defaults worth knowing

- Explore: 3 frames per direction, 1K, 1:1, about $0.07 a frame
- 4K render: about $0.24 a run, one run at a time
- Finish: falloff 0.75, horizon 0.16 (felt more than seen), canvas 6704
- Budget: $30 a month

All of it is in `heroshot.json`.
