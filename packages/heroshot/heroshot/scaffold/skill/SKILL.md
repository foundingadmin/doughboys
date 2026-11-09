---
name: heroshot
description: Build or continue an AI product photo for a series (album covers, product lines, campaign sets), from low res explore frames through an approved 4K render to a finished square master with a rebuilt backdrop, reviewed in Figma and handed off. Use when someone says "explore <item>", "next item", "run the 4K", "finish <item>", "place <item>", "build the next cover", or names an item from heroshot.json plus a step.
---

# heroshot · series photo playbook

The project's `heroshot.json` holds the config and every item's state. `heroshot status` reads it. Each step below is one `heroshot` command that writes files where the project keeps them and records what happened, so a later session resumes from an item's `status` and `next`.

The approver is `approver` in heroshot.json. **They approve at four gates. Never pass a gate without their yes in this conversation.** Before every 4K run, first or re-run, point them to the chosen explore frame on its review board and get a fresh written yes, even if it was approved in an earlier session. Quote it in `--approved`.

## Before anything

1. Read `heroshot.json`, the brief (`<dir>/docs/brief.md`), the series lock (`<dir>/prompts/explore/series-lock.md`) and lessons (`<dir>/docs/lessons.md`).
2. Session smoke test: `heroshot doctor`. One line per result. A network error means the environment must allow `generativelanguage.googleapis.com`. If Figma tools are missing, say so in one line and keep going with everything that does not need Figma.

## 0 · Find the item

- No item named: `heroshot status`, take the first item in order that is not placed. Say which and why in one line.
- An item named: `heroshot status ID`, pick up at its `status`.

| status starts with | go to |
|---|---|
| not started, exploring | 1 Explore |
| exploring, round R ready | wait for the pick, then 2 Lock |
| source approved | 3 Hi res prompt |
| rendered | 5 Check |
| master ... finished | 7 Review the finish |
| placed | 9 Hand off |

## 1 · Explore

1. `heroshot prompt ID --round R` drafts `<dir>/prompts/explore/<slug>-round-R.md` from the series lock with the item's subject, shape and ground filled in.
2. Rewrite every bracket as plain prose. Name the subject part by part, give real proportions, describe this item's own silhouette. Follow the series lock rules word for word.
3. `heroshot explore ID --round R` makes 3 frames at 1K on the fast model plus a contact sheet. One direction per run, only the rounds the approver asks for. Two directions side by side make a board of 1 to 6. Use `--dry-run` to see the cost first.
4. **Changing one thing on a picked frame** (a different product, a new color): write a prompt that opens "Keep this exact photograph and replace only the <thing>", restate what stays, and pass the pick with `--ref`. Everything else holds frame for frame.
5. Look at every frame yourself. Build a review board (`reference/figma.md`): frames numbered, a line under each on what works and what is off (subject real and complete, silhouette right, nothing cropped, no light fixture in the corners, no stray text).
6. Commit and push. Give the approver the board link. **Gate 1: they pick a frame** or ask for another round with notes. Fold the notes into round R+1.

## 2 · Lock the source

`heroshot lock ID work/<slug>/round-R/0F.png --pick RR-F`. Commit.

## 3 · Write the hi res prompt

Write `<dir>/prompts/hires/<slug>.md`, shaped like `<dir>/prompts/hires/_example.md`. Open with "Keep this exact photograph", then list every fix by name: exact label words, real dial numbers, every screen and what it shows or that it is plain. Specific beats simple. Add the item to the brief's queue. **Gate 2: show the approver the prompt.**

## 4 · Render 4K

Gate first: link the explore frame on its board and get the fresh written yes. Then `heroshot render ID --approved "<their words>"`. It crops tight to the subject at the closest supported aspect (every pixel of empty backdrop is detail thrown away), runs the pro model at 4K once, saves `<slug>-render-4k-<aspect>-<letter>.jpg`, logs the spend with the approval, and cuts a 3 by 2 grid of native check crops into `work/<slug>/check`. One run at a time. Look at it, then ask again.

Read the crop first: nothing cut off, floor shadows kept.

## 5 · Check

Look at each render full size and in crops: every label and button, edges, the top corners for a light fixture, any screen for fake text. Build a review board: renders side by side, matched crops in pairs at native pixels, pass or fail under each, the passing one marked. If something fails, sharpen the prompt and ask before re-running. Two sharper re-runs at most, then bring the best with the flaw named. For small print, feed the best render back with `--source <render> --no-crop` and a prompt that changes only the printing. **Gate 3: the approver picks the render.**

## 6 · Finish

`heroshot finish ID --render <dir>/assets/<slug>/<render>.jpg`

It rebuilds the backdrop as one smooth gradation of the item's swatch (falloff and horizon from heroshot.json `finish`), keeps the subject, contact shadows and grain, and writes the master, seam crops, 4:5 and 9:16 framing and a 4096 upload copy. Read `flags`: glow deltaE under 3 matches the swatch, hue spread near 0, `device_touches_edge` true means the crop cut the subject (back to 4). The subject itself is never touched.

Once the approver loves a finished master, `heroshot template <master>` makes it the falloff every later finish follows, so the series reads as a set. Only on their say.

## 7 · Review the finish

Board: the master next to the last approved master, swatch chips in the top corners and behind the subject, a swatch bar under each, plus native crops of the subject edges and the floor. **Gate 4: the approver says yes** or names the change (`--falloff`, `--horizon`, or a re-render).

## 8 · Place

Place the 4096 copy in the project's layouts (`reference/figma.md`, Placing a master). Use `framing` from the item's state for 4:5 and 9:16 crops. Screenshot the result and look at it: type and stickers clear of the subject, ground continuous. Set the item's `status` to `placed`.

## 9 · Hand off

Attach the picked render and the master to your reply with SendUserFile (`display: attach`) so the approver can grab them. If Drive is wired, `heroshot drive ID` saves both to the item's folder (`reference/drive.md`). Commit, push, say the item is done with the link.

## Rules that hold every step

- **Spend.** Every paid call is logged in `<dir>/spend.csv`. `heroshot spend` shows the month against `budget_usd_month`. A run that would cross it stops until the approver says go over (`--over-budget`). Explore stays on the fast model, 3 frames per direction.
- **Reviews happen on a board**, never only in chat. Repo copies of board screenshots under `<dir>/review/<slug>/` are the backup.
- **Docs move with the work.** A step is not done until `heroshot.json`, the brief and lessons agree with what happened. Add a dated line to lessons whenever a tool, model or step fails or surprises you, and fold prompt lessons into the series lock.
- **Never** store an API key or token in a file, a commit or a message. Keys live only in the environment.
- Never ask a generator for people, hands, real logos or readable text in explore. The hi res prompt supplies exact words.
