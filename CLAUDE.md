# Doughboys · operating manual for Claude Code

Release art for **The First Batch** by **Chillsbury Doughboys** (CBDB). Josh Titus is the creative director. You are the production line: low res explore frames in, finished 6704 square masters out, placed into the Figma covers.

Read this file, then `the-first-batch/tracks.json` (the state of all nine tracks), then `the-first-batch/docs/art-direction.md` before making images.

## How Josh works

- Open every reply with the date and Denver local time, like **Thu Oct 29 2026 · 9:14 AM MDT**.
- Never use em dashes or en dashes. Keep colons, semicolons and parentheses to a minimum.
- Terse. Lead with the answer. Spell out an abbreviation the first time it appears.
- No decorative emoji.
- Make the call and state it. Ask only when a choice is expensive to undo or truly his (which frame to pick, whether a 4K render passes).
- **Every image Josh reviews is assembled in Figma** on the Review page, never only in the repo or in chat. One board per review, options side by side, matched crops at native pixels, a pass or fail note under each. Build it with `pipeline/figma_review_board.js` (see `docs/figma.md`), screenshot it, and give Josh the board link. Repo copies under `review/` are the backup (Josh, Oct 29 2026).
- Punk rock = simple = results. Fewest moving parts that work.
- Cross-check every date you write.
- Never abbreviate the album name. The band abbreviates to CBDB. Catalog numbers run CBDB 00 (album) and CBDB 01 to CBDB 09.
- Images are generated. There is no photoshoot.
- Never store an API key or token in a file, a commit or a message. Keys live only in the environment.

## Where things live

| What | Where |
|---|---|
| Figma file (source of truth for all layouts) | https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee · file key `lcNDgyPE02C9Ldw8n2THee` |
| Figma pages | Toolkits `114:2` (variables and components), Brand Guide `114:3`, Album Art `114:4`, Review `128:77` (review boards, newest at the bottom), Archive `0:1`. Leave Archive alone, it holds the original explore frames |
| Team deck presented Oct 29 2026 | Google Slides `1FnuvkwDyWIgLbgMDZ8E7Lx6Ik2G6qNe2_kc-uMnwPJQ` |
| Long term storage | Google Drive folder `1QdToArron7EKW16mC68ViS1RBzONWV-i`, Track Covers `1g-RHVswNtj1Jp1VKjKmd3OZwDprvnKfB`. Each track folder holds **Masters**, **Exports** and **Archive** (Josh's old manual step folders, never delete). Ids are in tracks.json |
| Pipeline code | `pipeline/gen.py` (Gemini), `pipeline/finish.py` (expand, recolor, export), `pipeline/backdrop_template.py` (falloff template from Deluge v1), `pipeline/check.py` (review crops), `pipeline/framing.py` (Post and Canvas crop for Figma), `pipeline/figma_review_board.js` (Review boards) |
| Track state | `the-first-batch/tracks.json`. Update it and commit whenever a track moves forward |
| Approved 4K prompts | `the-first-batch/prompts/4k/` |
| Explore prompt blocks | `the-first-batch/prompts/explore/series-lock.md` |
| Art direction (the brief) | `the-first-batch/docs/art-direction.md`. Josh's master brief, the same file he keeps for the creative brief. Keep it current, see below |
| Lessons learned | `the-first-batch/docs/lessons.md`. Add to it when something fails or surprises you |
| Figma wiring recipe | `the-first-batch/docs/figma.md` |
| Review images | `the-first-batch/review/NN-track/`. Check crops and Figma board screenshots Josh looks at |

## Session start · smoke test

Run these first and report one line each.

1. `pip install -r requirements.txt` (rembg pulls its model weights from GitHub on first use)
2. `python3 pipeline/gen.py models` lists the image models your key can reach. If `gemini-3-pro-image-preview` moved, pass the new id with `--model` or set `TFB_RENDER_MODEL` and `TFB_EXPLORE_MODEL`.
3. Figma `whoami`, then `create_session` on file `lcNDgyPE02C9Ldw8n2THee`. Load the figma-use skill before any `use_figma` call.

If step 2 fails with a network error, the environment needs `generativelanguage.googleapis.com` on its allowlist. If the Figma tools are missing, the Figma connector is not attached to this session. Say so in one line and keep going with everything that does not need Figma.

Network this workflow needs: `generativelanguage.googleapis.com` (Gemini), `mcp.figma.com` and `www.figma.com` (Figma asset upload and image download), plus GitHub and PyPI (usually on by default).

## The per track flow

Josh will usually open with a track and a step, like "Traycee, run the tight crop 4K" or "Determinator, explore round 3". Look the track up in tracks.json and pick up from its `status`.

1. **Explore.** Build the prompt from `prompts/explore/series-lock.md` plus the track's device, dough silhouette and ground from tracks.json. Run `gen.py explore --n 6 --out work/NN-track/round-X`. Build a Review board in Figma with the frames numbered 1 to 6 and a line under each on what works and what is off. Commit the contact sheet to `the-first-batch/explore/NN-track/round-X/contact-sheet.jpg` as the backup, push, and give Josh the board link. He picks by number.
2. **Lock the source.** Copy the pick to `the-first-batch/assets/photos/NN-track/NN-track-source-<id>.png` and commit it. The repo keeps every approved source so a new session can resume.
3. **Write the 4K prompt.** Opens with "Keep this exact photograph" and lists every fix by name: exact label words, real dial numbers, which drip to remove. Specific beats simple. Save it to `the-first-batch/prompts/4k/NN-track.md`. Show it to Josh before spending a 4K run unless he already approved it.
4. **Crop tight.** `gen.py crop --source S --out C` crops to the device with a thin strip of backdrop and picks the closest supported aspect. Every pixel of empty backdrop is device detail thrown away. Read the crop and confirm nothing is cut off, including floor shadows.
5. **Render 4K.** `gen.py render4k --source C --prompt-file P --out R`. Expect about 5504 × 3072 at 16:9, 5056 × 3392 at 3:2, 4096 square at 1:1.
6. **Check.** Look at the render yourself at full size, in crops (labels, buttons, dough edges, frame edges, top left corner for a softbox). Build a Review board in Figma: full frames side by side, then each check crop as a matched pair at native pixels, a pass or fail note under each. Commit the crops to `review/NN-track/` as the backup and give Josh the board link plus a short pass and fail list. Re-run with a sharper prompt if something fails. Josh gives the final yes.
7. **Finish.** `python3 pipeline/finish.py R.png "#HEX" the-first-batch/assets/photos/NN-track/NN-track-final-v1.jpg` with the track's `ground_hex`. It takes a few minutes on CPU. It isolates the device, shifts the render's backdrop so the glow lands on the swatch, places the render at 1:1 on a 6704 canvas, and builds the rest of the backdrop from the Deluge v1 falloff template (`pipeline/backdrop_template.npz`) colored to the swatch. The device is never touched. Export is a JPG of about 13 MB. It prints a JSON report: `deltaE_glow_vs_swatch` under 3 is a match, `corner_L_minus_glow` should read about -29 -32 -5 -10 like Deluge, and `device_touches_edge` true means the crop cut into the device, so go back to step 4. Only rebuild the template if Josh approves a new reference master: `python3 pipeline/backdrop_template.py MASTER.jpg`. Run `python3 pipeline/check.py MASTER.jpg --ox X --oy Y --w W --h H --name work/NN` using the report's `offset` and `render` size, and look at the seam crops. Put the finished master on the track's Review board next to Deluge v1 so Josh judges the falloff by eye.
8. **Place in Figma.** Follow `docs/figma.md`. Upload the master and drop it into the **Photo slot** on the track's Cover, Post and Canvas instances as a free image layer (`pipeline/framing.py` gives the Post and Canvas offset), turn off Show placeholder, then screenshot the three boards and look at them. Josh can move and scale the photo on any instance without detaching.
9. **Commit and hand off.** Commit the master, the prompt and the tracks.json update, push, and tell Josh it is ready. Exports are preset on every board in Figma (cover JPG 3000 square, post 1080 × 1350, Canvas 1080 × 1920). Josh exports them and drops the master and exports into the track's Masters and Exports folders on Drive, unless a Drive upload path is available in your session.

## Keeping the docs current

Three files carry state between sessions. A step is not done until all three agree with what happened. Update them in the same commit as the work.

1. **`tracks.json`** · machine state. `status`, `next`, hashes, transforms, file paths.
2. **`docs/art-direction.md`** · Josh's brief, read by people. Update when a track moves forward or a rule changes:
   - **Track list** line for that track: where it stands and the date.
   - **4K queue**: add a track when its source and prompt are approved, change its heading when a run happens, remove it once the master is placed in Figma.
   - **Workflow**, **Series lock** or **Locked decisions** only when Josh sets or changes a rule. Quote his call and date it.
   - Bump the `Updated` date on line 3.
   - Keep his voice. Same terse style as the rest of the file, no em or en dashes, dates written like Oct 29 2026.
3. **`docs/lessons.md`** · add a dated line whenever a tool, model or step fails or surprises you. If the lesson changes how prompts are written, also fold it into `prompts/explore/series-lock.md` or the brief.

Before ending a session, run `git status` and `git diff --stat` and confirm all three moved if the work moved. Josh may upload a newer art-direction.md at the start of a session: diff it against the repo copy. His edits win. Keep any session updates his copy does not contradict, commit the merge, and hand him the merged file.

## Fallbacks

- **Gemini blocked or out of quota.** Figma Weave can run the same model (fal-ai/nano-banana-pro/edit, model id `af5a6789-c7af-4c46-9a42-70222654e55b`, 23 credits per 4K run). Every Weave run costs Josh credits, so ask before each one.
- **Figma upload blocked.** Commit the master and tell Josh the image is ready to drop into the Photo layer by hand. Give him the Post and Canvas crop numbers from framing.py.
- **A render keeps failing the check.** Two sharper re-runs, then bring Josh the best one with the remaining flaw named. Small last fixes can go to Josh in Photoshop.

## Git

- Work on `main` unless Josh asks for a branch. Commit small and often with plain messages like `Traycee: 4K tight crop render, check crops`.
- `work/` is scratch and is ignored. Everything Josh might want later lives under `the-first-batch/`.
- Files over 50 MB stay out of git. A 6704 master is about 12 MB, fine.
