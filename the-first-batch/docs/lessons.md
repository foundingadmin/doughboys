# Lessons

Newest at the bottom of each section. Add a dated line when something fails or surprises you.

## Resolution

- Upscaling a low res render does not work. Topaz Gigapixel invented grille and panel detail on Deluge (Oct 18 2026). Detail has to come from a 4K generation edit of the approved frame.
- The 4K pass spends about the same 17 megapixels on any aspect. A square run of Traycee left the computer at about 87 percent of 4096 and the rest went to backdrop. Crop tight first, at the closest supported aspect (Josh, Oct 28 2026).
- Deluge v1 is the 5056 × 3392 render placed untouched at 1:1 on a 6704 canvas, offset 824, 1656, with Photoshop Generative Expand filling the rest. Found by feature matching, scale 1.000 (Oct 28 2026). finish.py does the same placement.

## Finish pipeline

- A global blur plus a straight line fit of the backdrop extrapolated wildly, white at the bottom and deep blue at the top. Anchoring the extension to the render's own border and continuing each edge's falloff fixed it.
- A smooth fill leaves a visible step at the seam because the render's backdrop has grain and mottle. finish.py synthesizes texture from the render's own backdrop spectrum.
- Scaling chroma blew the gamut in the corners. Josh's correction behaves like a colorize: keep lightness shape, pull chroma to the target almost flat, shift hue. That is what the recolor does now.
- Measure the glow only on real render pixels inside Josh's check ellipse, never on the generated extension.
- Calibration on Deluge: backdrop color inside the render lands within deltaE 2.2 of Josh's hand made v1.
- finish.py crashed on `"#73D2AB"` because it parsed the hex without stripping the `#`, though CLAUDE.md passes it that way. Fixed to accept both (Oct 29 2026).
- A render whose glow is much lighter than the swatch finishes too dark. Traycee B glowed at L 86 against Mint at L 78, finish.py fit a lightness gamma of 1.74, and the corners and extended floor went deep green with dark streaks while the glow still measured deltaE 1.69. deltaE alone does not pass a finish. Look at the full frame next to Deluge (Oct 29 2026).
- Root cause of that failure, found Oct 29 2026: finish.py extended each render edge by extrapolating its lightness slope, so a bright floor glow at the bottom edge became a dark streak further out, and the gamma curve then stretched every dark. Josh called it terrible.
- The fix, set Oct 29 2026: every cover's backdrop falls off like Deluge v1. `backdrop_template.py` measures Deluge v1's lightness and hue relative to its glow, finish.py colors that to the swatch, shifts the render's lightness instead of curving it, and hands the broad light from render to template on a smooth radial weight, inside the render too, so the render's rectangle never shows. Shadows, mottle and grain stay the render's own. Traycee B: glow 1.0 off Mint, corners -29 -31 -5 -10 against Deluge's -32 -33 -6 -11.
- First pass of the template left a faint box at the render's border because only the extension followed the template. Blending the broad light inside the render's backdrop as well removed it (Oct 29 2026).
- Same depth reads darker on Mint than on Bondi. Josh found Traycee's corners a bit too dark at full Deluge depth, so finish.py got `--falloff` (Oct 29 2026). Review boards for color now carry swatch chips over the image and a swatch bar under it.
- Josh saw several slightly different greens in the Traycee backdrop (Oct 29 2026). Measured in OKLab the hue drifted 12.4 degrees, yellow green in the corners, bluer on the floor, from the render's own light, the template's hue drift and CIELab hue bending with lightness. Deluge v1 holds 3.7 degrees with flat OKLab chroma. Fix: a last pass keeps each backdrop pixel's OKLab lightness and takes hue and chroma from the swatch. Spread now 1.7 degrees measured on the JPG.
- Scaling the swatch by luminance in linear light also gives one hue, but it greys the dark corners and pulled the Deluge regression to deltaE 8 in the margins. Constant OKLab chroma is what Josh's v1 does. Check device edges after any backdrop pass, and run no more than three finish.py jobs at once on a 16 GB container, a fourth was killed for memory.
- Even with one hue, Josh still saw hotspots: bright patches above and under the computer, dark vertical bands at its sides (Oct 29 2026). They were the generator's own lighting, kept because the finish blended the render's backdrop into the template. His Deluge backdrop is a smooth Photoshop gradation with none of that. Fix: finish.py rebuilds the backdrop entirely from the template and keeps from the render only the device, contact shadows (darkening only, at each column's floor line and within about 1 percent of the device) and grain. Device edge pixels are decontaminated against the old backdrop so no old color clings to them.
- Contact shadows computed on the 8x low res grid came out as a dotted line, and a dilated device mask skipped the darkest pixels right at the contact and left a light ring. Compute shadows at half res with a tight mask.
- Josh wanted a really subtle cyclorama horizon so the smooth backdrop reads as a sweep (Oct 29 2026). finish.py `--horizon` darkens a soft band, tight above and long below, placed 3 percent of the canvas above the highest floor contact so it always passes behind the device. At 0.16 it vanishes at thumbnail size, 0.25 reads at cover size, 0.35 starts to read as a seam.
- Josh picked depth 0.75 and cyc horizon 0.16 on Traycee (Nov 8 2026). They are now finish.py defaults. At 0.16 the horizon is felt more than seen, which is what he wanted.
- The Drive connector cannot carry masters. An Apps Script web app running as Josh (`pipeline/drive_drop.gs`) takes the upload, keyed by an environment variable and limited to the Track Covers tree (Nov 8 2026).
- On Canvas 9:16 a wide device set clips at the sides. The Photo slot lets Josh scale it, so place it at the default framing and say so (Traycee, Nov 8 2026).
- Attaching the master and render to the chat reply with SendUserFile, plus a link to the Masters folder, was the fastest Drive hand off for Josh (Nov 8 2026). It is now the standard, alongside the Drive drop upload.
- Never take a median of hue angles. They wrap at 180 degrees and Traycee's grey glow sat right on the wrap, so the hue came out 40 degrees off. Take the median of Lab a and b, then the angle (Oct 29 2026).
- Regression test for any finish.py change: re-finish Deluge from `01-deluge-4k-render.jpg` with #65B8E5 and run check.py against v1. Oct 29 2026 baseline: deltaE 2.4 inside the render, 2.8 in the margins.

## Crop and 4K

- `gen.py crop` picked 3:2 for Traycee, not the 16:9 the brief expected. The device box is about 1.59 wide, so 3:2 keeps more pixels on the device. Trust the auto pick unless something gets cut (Oct 29 2026).
- 4K edits turn small screen UI into fake text. On Traycee the taskbar grew a garbled Start label and clock, and the CD player buttons got smudged glyphs. Name every UI strip in the 4K prompt and say exactly what it shows, or that it is plain (Oct 29 2026).
- Naming them fixed it in one re-run: the transport buttons came back as clean play, pause, stop and eject symbols, the taskbar went plain, and asking for one solid column closed the hole in Traycee's dough (render B, Oct 29 2026).
- Gemini returns JPEG bytes even when `gen.py` saves to a `.png` name. Store renders in the repo as `.jpg`, untouched (Oct 29 2026).

## Docs

- CLAUDE.md now says how to keep art-direction.md, tracks.json and this file current. Update all three in the same commit as the work (Oct 29 2026).

## Prompts

- Specific beats simple. Naming every label word, dial number and drip to remove worked on Deluge (Oct 18 2026).
- The explore lessons (softbox, raised camera for turntables, no pink cast, own silhouette per track) live in prompts/explore/series-lock.md.

## Tools and network

- Gemini image API needs `generativelanguage.googleapis.com` allowed in the environment. Figma asset upload posts to `mcp.figma.com`, image downloads come from `www.figma.com`.
- Weave in Figma runs the same Nano Banana Pro edit model for 23 credits per 4K run. Fallback only, ask Josh before each run.
- Large binaries cannot go through the Drive connector, it passes file contents through the conversation. GitHub is the hand off for masters. Server side Drive copies of files already on Drive are fine.
- Chat uploads shrink loose images to 2576 px. Full size files travel zipped, or through the repo.

## Figma

- See docs/figma.md. Scripts are atomic, pages reset per call, fonts load before any text change.
- `upload_assets` caps a file at 10 MB, so a 12 MB master will not go. Figma also stores images at 4096 px max. Upload a 4096 square JPG q95 downscale of the master (about 2.4 MB for Deluge). The repo and Drive keep the full 6704 (Oct 29 2026).
- Josh reviews in Figma, not on GitHub or in chat. Every review gets a board on the Review page (Oct 29 2026).
- `upload_assets` with `nodeIds` drops each image straight into an existing rectangle, so build the board first and upload into its slots. 16 images in parallel took a few seconds (Oct 29 2026).
- Josh renamed Kit to Toolkits and Page 1 to Archive, and added a `---` divider page (seen Oct 29 2026).
- A plain image fill on a component layer can be swapped on an instance but never moved or scaled. Josh needed to reposition the Deluge boombox, so Photo became a slot on Oct 29 2026. Slot content on an instance is free to move, scale and swap.
- `upload_assets` without a target node drops a new frame on the page. Delete it in the same `use_figma` call that fills the boards (Oct 29 2026).

## Nov 8 2026 batch (Spice, Bopkins, Suavecita 4K, explore 06 to 09)

- The "compressed preview" note on Spice, Bopkins and Suavecita was half right. Figma's raw image fills are 1024 JPEGs whose SHA1 equals the recorded `image_hash`, so they are the true originals, and the repo jpgs were a re-encode. Pull the raw fill with `download_assets` and check the hash (Nov 8 2026).
- Small printed words fail at 4K even when named. Bopkins buttons came back as mush on four of six runs. Two things worked: telling a surface it is plain ("plain brushed aluminum with nothing printed on it" cleared the plate and the knob), and asking for words in bold black capitals that fill most of the button (F printed START, STOP, 33, 45). Each pass can also bring back something an earlier pass fixed, like the lid badge on C and F (Nov 8 2026).
- "Keep this exact photograph" anchors screen content. Suavecita's LCD icons survived six runs, including "redraw the LCD from scratch and replace every icon". Fix screen content in the source before the 4K run, or in Photoshop after (Nov 8 2026).
- `cover.py` loads tracks.json at the start of a step and saves it at the end, so two steps in parallel lose one update. Chain cover.py steps, and run parallel explores through `gen.py explore` directly, then record state (Nov 8 2026).
- Explore wording: "rope" made Mancub's spill a snake, "stacked mound" made Show Me Your Love's mound coil like soft serve. Both fixed in one round, rules folded into series-lock.md (Nov 8 2026).
- Josh wants Review boards in one row left to right, newest at the right, not stacked in a column. Moved all thirteen and changed `figma_review_board.js` to place new boards after the rightmost one (Nov 8 2026).
- finish.py filled every enclosed hole as device, so the Spice headphone cord loop kept a D shaped patch of old render backdrop. It now opens a hole of 400 px or more (at 1600 wide) whose median Oklab color sits within 8 of the backdrop at the same height. Spice opened at 0.9 to 4.7, Suavecita's chain loop at 4.7, real device holes on Bopkins and Suavecita read 14 and up, Traycee has none (Nov 8 2026).
- Small print fix that worked on Bopkins: feed the best render back in as the source with a prompt that changes only the printing, every mark spelled out. G came back fully clean. Rendering a crop of just the controls at 4K also works (about 4x the pixels per letter) and is the fallback if a full frame pass garbles (Nov 8 2026).
- Gemini prepaid credits ran out mid batch (HTTP 402 RESOURCE_EXHAUSTED). gen.py prints the error and stops. Top up in AI Studio, or ask Josh before any Weave run (Nov 8 2026).
- Iconic devices need the real thing described part by part from a reference photo, and the reference camera angle. The 1985 clock radio and the 1993 Talkboy both landed on the first round that way (Nov 8 2026).
- Spend, Nov 8 2026: about 79 calls in one afternoon, roughly $12.50 at list price against a $30 monthly limit. 60 Pro explore frames were two thirds of it, 18 4K runs the rest. Two unrequested rounds (Mancub R2, Show Me Your Love R2) were rejected. Since then: Flash for explore, 3 frames per direction, rounds only on request, and every 4K behind a fresh written yes (Josh). `the-first-batch/spend.csv` logs every call.
- Josh changed the Review layout again the same day: one column per track in album order, rounds stacked top to bottom. The board script now re-lays the whole page by the `CBDB NN` name prefix after each new board, so the layout holds whatever gets added (Nov 8 2026).
- finish.py grain came out streaky on Bopkins G: the mean spectrum picked up the long horizontal floor shadows. Now median across patches and averaged around each radius, so grain has no direction (Nov 8 2026).
- A clear part (Bopkins dust cover) keeps the old render backdrop behind it, which reads as a lit box against the deeper new falloff. `--glass-box x0,y0,x1,y1` relights the see-through pixels to the new backdrop in linear light, keeping the acrylic edges and reflections. A tight color cutoff (12) left the bright glow band patchy, 30 with a wider blur relit it evenly; the hinges and tonearm stay out (Nov 8 2026).
- Cheap fine tuning works best as Flash edits of the picked frame (`gen.py explore --ref FRAME`), one prompt per variation. The device holds and only the named thing changes. Watch for drift: Mancub v6 turned the buttons maroon, Determinator creased and rustic dough read as faces (Nov 8 2026).
- Swatch chips on finish boards carry no stroke: a white outline separates the chip from the backdrop and hides the match Josh is judging (Nov 8 2026).
- Show Me Your Love: fresh text to image from a part by part description of the reference beat edits of an earlier frame, whose wrong geometry anchors the device. Edits keep the dough, fresh frames get the device. Combine them in a second cheap step (Nov 8 2026).
- finish.py copied texture up to 48 px across as grain, and the Determinator render's soft backdrop mottle came through as blotches. Grain is now taken below 12 px only (GRAIN_SIGMA), the backdrop reads smooth like Deluge (Nov 8 2026).
- Flash edits will not change a device's proportions: asked to widen the Boombap radio by a tenth to two fifths, all six came back within 2 px of the original. Widen in code instead (stretch a plain band of the face), then one Flash pass to straighten the bent edges. +10 and +20 percent came back clean, +30 and +40 kept the bend (Nov 8 2026).
- A stringy looking tail can be what Josh likes: the R4-1 finger smear on Mancub, which I had called a fail. Flag it, do not discard it (Nov 8 2026).
- Passing Josh's close up photos of the real device as extra references to the 4K edit (`--ref`) got small printed words right in one run on Mancub: DOT MATRIX WITH STEREO SOUND, BATTERY, B and A, START. Only a tiny molded marking missed. Ask for detail photos before a 4K on any device with printed text (Nov 8 2026).
- Multi image Flash edits copy the body of every whole frame passed in. Show Me Your Love round 6 drifted to R5-1's wrong body twice when R5-1 and R5-4 went in whole. Passing only cropped parts (the dough, the keys, the button strip) kept R5-6's device. Crop references to the part you want (Nov 8 2026).
- Bopkins style text pass worked again on Boombap: SLEEP, WAKE, HOUR, MINUTE and ON, OFF, MUSIC, ALARM came back clean in one run. Placement words ("centered on the top face of the bar") are weaker than spelling, SNOOZE landed on the bar but off center (Nov 8 2026).
- The container clock is UTC, so after 5 PM in Denver it reads tomorrow. cover.py and the spend log now take the date from America/Denver. Check `TZ=America/Denver date` before writing any date (Nov 8 2026).
- A slot property added on the component set with `addComponentProperty(name, 'SLOT', '')` and bound to a plain frame in each variant through `componentPropertyReferences = { slotContentId }` turns the frame into a SLOT, and every existing instance picks up the default content at its old position. Used for the Fresh Batch sticker, 18 Cover and Post instances, nothing shifted (Nov 8 2026).
- Nov 8 2026 · Behind the scenes side project. Flash explore with the Deluge cover passed as `--ref` held the boombox and dough shape at set scale in all six frames, garage clutter and lighting gear came out convincing on the first pass. Watch for real brand logos on props (a shipping box smile showed up in frame 4) and garbled flour bag labels. Prompts live in `prompts/bts/`.
- Nov 8 2026 · Behind the scenes round 2. Passing Josh's round 1 pick as a second `--ref` held the layout and still let the model strip the garage bare. Without it the model invented its own layout and drifted toward real looking flour brand marks ("GOLD"). "No brand logos on any product" in the prompt was not enough on its own.
- Nov 8 2026 · Behind the scenes round 3. Four `--ref` images on Flash (cover, layout, Josh's own steel table, a cropped TV tray) worked: the props swapped in on 5 of 6 frames. Drift to watch: a steel table grew a wood top, the tray got a plastic top. Product photos on white made cleaner prop references than crops from earlier frames.
- Nov 8 2026 · Behind the scenes round 4. A "Keep this exact photograph, change only" edit on Flash swaps materials (plastic sawhorses to pine) but will not move an object across the frame: the TV tray stayed behind the tripod on all three edits. A rebuild with the frame as a layout reference moved it on 1 of 3. For repositioning, rebuild; for material swaps, edit.
- Nov 8 2026 · BTS pipeline, Mancub round 1. With the environment frame as a reference, Flash copied its camera angle in all six frames even though each prompt named a different one. Fix in round 2: say outright that image 2 shows what things look like, not where to stand, and write each variation as a concrete move (2 m right and 30 degrees left, knee height, step stool corner). All six then differed.
- Nov 8 2026 · BTS Mancub round 2. The seamless paper came out pale mint against the cover's muted lime, even with the hex and "match image 1". The bounce card dropped out of the wider angles, and one close up mixer carried a real brand name. Both are now spelled out in `prompts/bts/environment.md`. Paper color is still open.
- Nov 8 2026 · BTS round 1 for Spice, Bopkins, Traycee, Determinator and Boombap through bts.py, variations spread across tracks. 13 of 15 frames held the room and kit. Warm and pastel papers (butter, bubblegum, mint, tangerine) came out true. The muted cool ones (blueberry here, lime on Mancub) drift paler and brighter. Strays to watch: wood trestles instead of the metal sawhorses on a high angle, a shelf of branded boxes at a frame edge.
- Gemini key lives only in the "Gemini API Access" cloud environment (GEMINI_API_KEY). A session started on Default cannot generate. Start image sessions there (Nov 8 2026).
- Nov 8 2026 · Album cover explore round 1, six top down directions on Flash at 1:1. "Edge to edge" dough still showed dark corners where the slab domed, or the whole slab on a paper border: crop in or say the camera sits close enough that the dough runs past every edge. A cassette "pressed in and lifted away" came back as a raised cassette cast in dough on all three, never a hollow. Cookie and portion grids held the wheel order with Mint in the middle on all six. Face watch: a smiley on one cookie, three finger dents on one lump, a sleeve cut out reading as a mouth.
- Nov 8 2026 · The Review page is now named "   ↪ Review", so `figma_review_board.js` matching by name would have made a second Review page. It now finds the page by id 128:77.
- Nov 8 2026 · Album cover round 2. The brand pinwheel drawn in code and passed as a second image held its order and angles on all three record edits and on two of three nine slice frames (one Blueberry wedge drifted to lavender). Text described color bands (cassettes, striped sweep) kept the order but pushed Cherry and Tangerine louder than the 500 steps: redraw flat color fields in code at finish rather than trusting the generator. The record label went loud orange on every edit. A top down vat still darkens the corners and still leaves some pieces lying on top. Type tests: a paper label carries its own background, so it held on every image; plain ink type got lost on busy grids and dark trays.
- Nov 8 2026 · `appendChild` returns nothing in use_figma scripts, so `const t = parent.appendChild(text(...))` is null. Create the node, append it, keep the original reference.
- Nov 8 2026 · `figma.createTextPath` moves the new text path onto the page, even when its vector sat inside a component. Read its x and y, append it back to the parent, set x and y again. To center curved text, measure the string as a plain text node first and build the arc to that length.
- Nov 8 2026 · A Figma text path will not rotate with the rotation property, and changing its font size shifts the text off center along the path. Recenter by rebuilding the arc to the measured text length, keeping the node's own font, size and spacing.
- Nov 8 2026 · Long fine print in a narrow centered block broke names across lines (THE / KEEP). Joining the words of each credit with non-breaking spaces, and the dot to the credit before it, makes lines break only after a dot, at any width.
