---
name: build-track-cover
description: Build or continue a track cover for The First Batch, from low res explore frames to a finished 6704 master placed in the Figma covers and saved to Drive. Use when Josh says "build a track cover", "next cover", "do the next track", "<track>, explore", "<track>, run the 4K", "finish <track>", "place <track>", or names a track and a step.
---

# Build a track cover

The per track playbook. CLAUDE.md is the manual and wins on conflict. Josh's voice rules apply to every message: date and Denver time first, no em or en dashes, terse, lead with the answer.

Every step has one command in `pipeline/cover.py`. It writes files where the repo keeps them and records state in `the-first-batch/tracks.json`, so a later session resumes from `status` and `next`. **Josh approves at four gates. Never pass a gate without his yes in this conversation.**

## 0 · Find the track

- "Build a track cover" with no name: run `python3 pipeline/cover.py status` and take the first track in album order that is not `placed`. Say which one and why in one line, then go.
- With a name or number: `python3 pipeline/cover.py status NN` and pick up at its `status`.
- Read the track's line in `the-first-batch/docs/art-direction.md` (Track list, 4K queue) before writing any prompt.

| status starts with | go to |
|---|---|
| not started, exploring | 1 Explore |
| exploring, round R ready for Josh | wait for his pick, then 2 Lock |
| source approved | 3 4K prompt, or 4 when `prompts/4k/NN-track.md` exists and the brief's 4K queue lists it as approved (Spice, Bopkins, Suavecita) |
| 4K rendered | 5 Check |
| master ... finished | 7 Review the finish |
| placed in Figma | 9 Hand off, or tell Josh the cover is done |

## 1 · Explore (low res frames to choose from)

1. `python3 pipeline/cover.py prompt NN --round R` drafts `the-first-batch/prompts/explore/NN-track-round-R.md` from the series lock, with the track's device, silhouette and ground filled in.
2. Replace every bracket with plain prose: name the device part by part, give real proportions, and describe this track's own dough silhouette. Follow `prompts/explore/series-lock.md` rules word for word. Never name a softbox, never ask for pink or gluten strands.
3. `python3 pipeline/cover.py explore NN --round R` makes 6 frames at 1K and the contact sheet.
4. Look at every frame. Build a Figma Review board: frames numbered 1 to 6, a line under each on what works and what is off (device real, silhouette right, dough firm, nothing cropped, no softbox in the corner, no text). Recipe in `docs/figma.md`, Review boards.
5. Commit and push. Give Josh the board link. **Gate 1: Josh picks a frame** (or asks for another round with notes; fold his notes into round R+1).

## 2 · Lock the source

`python3 pipeline/cover.py lock NN work/NN-track/round-R/0F.png --pick RR-F` copies the pick into the repo. Commit.

## 3 · Write the 4K prompt

Write `the-first-batch/prompts/4k/NN-track.md`. Open with "Keep this exact photograph", keep the tight framing, then list every fix by name: exact label words, real dial numbers, which drip or hole to remove, every UI strip and what it shows or that it is plain. Copy the shape of `prompts/4k/05-traycee.md`. Add the track to the brief's 4K queue. **Gate 2: show Josh the prompt** unless he already approved it.

## 4 · Crop and render 4K (automated)

`python3 pipeline/cover.py render NN --runs 2` crops tight to the device at the closest aspect, runs Gemini 3 Pro Image at 4K twice from the same prompt, saves both renders as `NN-track-4k-render-<aspect>-a.jpg` and `-b.jpg`, and cuts a 3 by 2 grid of native check crops per render into `work/NN-track/check`.

If the track's `source.note` says the repo copy is a compressed preview, pull the full original from its Figma node first (Archive page, `get_screenshot` of that node at its native size, or the image fill's download), save it over the source and pass it with `--source`.

Read the crop first: nothing cut off, floor shadows kept. If the crop step cut into the device, rerun with `--source` after fixing, or tell Josh.

## 5 · Check

Look at each render at full size and in crops: every label and button, dough edges and holes, frame edges, top left corner for a softbox, any screen or UI for fake text. Add targeted native crops for anything the grid splits. Build a Review board: full renders side by side, matched crops as pairs, a pass or fail note under each, the passing one marked. If something fails, sharpen the 4K prompt and run again: two sharper re-runs at most, then bring the best with the flaw named. **Gate 3: Josh picks the render.**

## 6 · Finish

`python3 pipeline/cover.py finish NN --render the-first-batch/assets/photos/NN-track/NN-track-4k-render-...-b.jpg`

It rebuilds the backdrop as Josh's smooth Deluge falloff in the track swatch (depth 0.75, cyc horizon 0.16, his defaults from Nov 8 2026), keeps the device, contact shadows and grain, and writes the master, check crops, Post and Canvas framing and a 4096 copy for Figma. Read its `flags`. Glow under 3 deltaE, hue spread near 0, `device_touches_edge` false.

## 7 · Review the finish

Build a Review board: the master next to Deluge v1 and next to the last placed cover (Traycee from Nov 8 2026), Mint and track swatch chips in the top corners and behind the device, a swatch bar under each, plus native crops of the device edges and the floor under the device. **Gate 4: Josh says yes** or names what to change (depth with `--falloff`, horizon with `--horizon`, or a re-render).

## 8 · Place in Figma

Follow `docs/figma.md`, Placing a finished master. Upload the 4096 copy, drop it into the **Photo slot** on the track's Cover, Post and Canvas (instance ids in `tracks.json` under `figma`), hide the placeholder, remove the upload frame, screenshot the track's section and look at it: sticker and title clear of the device, ground continuous. Wide devices clip on Canvas 9:16, say so, Josh can move or scale the image in the slot. Record the hash and image layer ids in `tracks.json`, set `status` to `placed in Figma`.

## 9 · Save to Drive and hand off

`python3 pipeline/cover.py drive NN` saves the picked 4K render and the master into the track's Masters folder on Drive and records the file ids. If it says Drive is not wired, follow `docs/drive.md` once, or commit and tell Josh to drop the two files into Masters by hand.

Update the brief (Track list line, remove the track from the 4K queue, Updated date), lessons if anything surprised you, and `tracks.json`. Commit, push, open or update the pull request. Tell Josh the cover is placed, give the section link, and that exports are preset on every board.

## Keep moving

When Josh says "build the covers" or "keep going", run tracks in album order and batch the waiting: start explore for the next track while he reviews the current one, and put each gate on its own board so he can answer them in any order. Never spend Weave credits without asking.
