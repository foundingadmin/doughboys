# The First Batch · Art Direction

Release artwork for The First Batch by Chillsbury Doughboys. Updated Oct 29 2026.

- [Creative brief](https://claude.ai/code/artifact/e34a1d07-501a-4033-ba3d-b4bcc4d3668e)
- [Figma](https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee) · source of truth from Oct 29 2026. Pages Kit (variables and components), Brand Guide and Album Art (album plus all nine tracks as Cover, Post and Canvas instances driven by one Track variable mode each). Page 1 keeps every generated test at full size
- [Production repo](https://github.com/foundingadmin/doughboys) · Claude Code runs the device photo workflow end to end from here. CLAUDE.md is the manual, the-first-batch/tracks.json holds each track's state
- [Design canvas](https://claude.ai/artifact/AKevZru2Tw5MbhUfXc8KkH) · retired Oct 29 2026, kept for reference

## 4K queue · approved frames waiting for their 4K run
Claude Code runs these from the repo (prompts/4k) through the Gemini API: tight crop, 4K edit, check, finish. Manual route if needed: crop tight, then Google AI Studio, Gemini 3 Pro Image (Nano Banana Pro), resolution 4K, aspect ratio matched to the crop, prompt pasted as an edit in the same chat.

### Spice · F2 · approved Oct 19 2026
- **Source image** · [Figma node 53:2](https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee?node-id=53-2), 1024 square. Also on the canvas Image Tests page, board "CBDB 02 Spice · E4 set"
- **Prompt**

```
Keep this exact photograph. Same camera position, framing, lighting, Walkman, headphones, dough, pool and backdrop. Do not move, redesign or restyle anything. Render it at 4K as a real photograph shot on medium format film for a 1990 mail order catalog, with fine film grain and crisp, true detail. Make only these fixes:

1. Cassette door: remove the small yellow tab on the left edge of the door so that edge is plain and flush. The door stays exactly as open as it is now, about 15 degrees, hinged on the right.
2. Dough: remove the thin threads pulling off the left side of the dough. It is one cohesive mass of raw kneaded bread dough, pale oatmeal beige, satin matte skin with fine stretch lines, no strings, no holes. Keep its shape, the pinch at the door edge, and the pool exactly where and how big they are now.
3. Tuner window: print a real analog tuner scale in the slim window across the top. Top row reads FM 88 92 96 100 104 108 MHz. Bottom row reads AM 530 600 800 1000 1300 1600 kHz. Small white type, fine tick marks, a thin red needle. No brand name or model number anywhere.
4. Top edge: four low profile dark grey rubber transport buttons, evenly spaced and barely raised, with a tiny red power light glowing beside them. The headphone plug stays seated in the jack.
5. Cassette window: dark smoked plastic set into the charcoal grey panel. Behind it, only the shadowy empty well and two reel spindles. No cassette.
6. Headphones: yellow headband, round orange foam ear pads, thin grey cord, all fully inside the frame with clear backdrop around them.
7. Backdrop: seamless butter yellow paper with a soft glow behind the device and on the floor, falling to a deeper golden yellow in the top corners. No studio equipment, no seams, no horizon line.

No people, no hands, no logos, no readable text other than the tuner scale.
```

### Bopkins (was Danish) · G1 · approved Oct 19 2026
- **Source image** · [Figma node 58:2](https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee?node-id=58-2), 1024 square. Also on the canvas Image Tests page, board "CBDB 03 Danish · round 1"
- **Prompt**

```
Keep this exact photograph. Same camera position, framing, lighting, turntable, raised dust cover, dough, pool and backdrop. Do not move, redesign or restyle anything. Render it at 4K as a real photograph shot on medium format film for a 1990 mail order catalog, with fine film grain and crisp, true detail. Make only these fixes:

1. Dust cover: remove the dark rectangular badge in the middle of the raised smoked lid so the acrylic is plain and clear.
2. Spindle: keep the center spindle poking up through the middle of the dough exactly as it is.
3. Tonearm: keep it exactly where it is, and let the stylus sink just slightly into the dough surface with a small soft dent around it.
4. Platter rim: crisp, evenly spaced strobe dots all the way around the silver rim.
5. Controls: the knob at the front left with a tiny red power light glowing beside it. The pitch slider and the row of small buttons at the front right stay as they are. Any small control labels read only 33, 45, START, STOP and PITCH. No brand name or model number anywhere, including the small plate at the front left.
6. Dough: one cohesive mass of raw kneaded bread dough, pale oatmeal beige, satin matte skin with fine stretch lines, no strings, no holes. Keep the flat record shaped pile, the pour off the front left, and the pool exactly where and how big they are now.
7. Backdrop: seamless bubblegum pink paper with a soft glow behind the turntable and on the floor, falling to a deeper rose pink in the top corners. No studio equipment, no seams, no horizon line.

No people, no hands, no logos.
```

### Suavecita · I4 · approved Oct 19 2026
- **Source image** · [Figma node 73:2](https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee?node-id=73-2), 1024 square. Also on the canvas Image Tests page, board "CBDB 04 Suavecita · lean back set"
- **Prompt**

```
Keep this exact photograph. Same camera position, framing, lighting, virtual pet, chain, dough and backdrop. Do not move, redesign or restyle anything. Render it at 4K as a real photograph shot on medium format film for a 1997 mail order catalog, with fine film grain and crisp, true detail. Make only these fixes:

1. Shell: translucent bubblegum pink plastic with crisp seams, the green circuit board, chip and coin battery showing faintly through it. No lettering, logo or model name anywhere on the shell or the board.
2. Screen: a crisp pale grey green LCD with a visible pixel grid. In the middle, the same tiny original pixel creature, a round blob with two dot eyes. A row of four simple pixel icons across the top (a bowl, a light bulb, a ball, a heart) and four across the bottom (a bandage, a speech bubble, a star, a sun). No characters from any existing game and no text.
3. Buttons: three round white buttons, evenly spaced.
4. Chain: the silver ball chain from the top loop, with crisp evenly sized beads, running down to the floor and staying fully inside the frame.
5. Dough: one cohesive mass of firm raw kneaded bread dough, pale oatmeal beige, satin matte skin with fine stretch lines, no strings, no holes. Keep the tall nest exactly as it is, with the egg leaning back in its hollow and the front lip folded down to the floor on the left. No pool, nothing runny or glossy.
6. Backdrop: seamless dusty cherry red paper with a soft glow behind the egg and on the floor, falling to a deeper cherry red in the top corners. No studio equipment, no seams, no horizon line.

No people, no hands, no logos.
```

### Traycee · 81:2 · first 4K run Oct 28 2026 · tight crop re-run next
- **Source image** · Josh's first AI Studio 4K render of [Figma node 81:2](https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee?node-id=81-2), cropped tight to 16:9 in Photoshop with a thin strip of mint on every side and the floor shadows kept. Josh moved Traycee from K4 (node 85:2) to 81:2 on Oct 28 2026. The square run left the computer at about 87 percent of a 4096 square, so the re-run spends the 4K output on the device instead of backdrop
- **Run** · aspect ratio 16:9, 4K. Expect about 5504 × 3072
- **Prompt**

```
Keep this exact photograph. Same camera position, lighting, tower, monitor, speakers, dough and backdrop, and keep this tight framing exactly as it is. Do not zoom out, add backdrop, move, redesign or restyle anything. Render it at 4K as a real photograph shot on medium format film for a 1996 mail order catalog, with fine film grain and crisp, true detail in every surface: the dough's stretch lines and folds, the drive bay edges, the speaker cloth and the monitor's plastic. Make only these fixes:

1. CD player window: remove the small icon at the right end of the title bar so the title bar is plain grey. The display still reads 05 and 00:00 in green digits, with the transport buttons below it.
2. Screen: remove the faint mark in the top left corner so the teal desktop is clean edge to edge.
3. Frame edges: every edge keeps a thin strip of seamless mint backdrop, with the floor and the soft contact shadows under the dough, tower, monitor and speakers. Nothing touches or crosses the edge of the frame.

No people, no hands, no logos, no readable text other than the CD player display.
```

## Concept
The dough is the media. The only way to play a Doughboys record is to stuff a wad of raw dough into your boombox where the cassette goes. Shot like a 1990 catalog page. Real ink, real paper, scanned for the archive. Nostalgia, youthful joy, fun, curiosity. Flat, dry, ironic humor.

## Device photo workflow · set Oct 18 2026
From Oct 29 2026 Claude Code runs every step below from the doughboys repo with the Gemini API, and Josh approves the pick, the prompt and the 4K check. Steps 4 to 6 no longer need AI Studio or Photoshop.

1. **Explore.** Claude generates batches (Gemini through Figma until Oct 29 2026, now the Gemini API with a numbered contact sheet) until Josh approves one as real and on brief. Every prompt opens with the series lock below.
2. **Write the 4K prompt.** Claude hands Josh a full prompt that opens with "keep this exact photograph" and then lists every fix by name: exact label words, real dial numbers, which drips to remove, which key is pressed. Specific beats simple, proven on Deluge Oct 18 2026. Approved frames and their prompts wait in the 4K queue above.
3. **Crop tight · set by Josh Oct 28 2026.** Before the 4K run, crop the source to the device's own shape with only a thin strip of backdrop on every side and the floor shadows kept. AI Studio spends about the same 17 megapixels on any shape, so every inch of empty backdrop is device detail thrown away. Pick the aspect ratio closest to the device: 16:9 for the boombox and the PC, 4:3 for the turntable, 3:4 or 4:5 for upright devices like the Walkman and the virtual pet. Backdrop for the cover comes back in the finish step.
4. **Render at 4K.** Claude Code sends the crop plus the prompt to Gemini 3 Pro Image (Nano Banana Pro) as an edit, resolution 4K, aspect ratio matched to the crop. Josh's manual route was the same run in Google AI Studio. Output at 4K is about 5504 × 3072 at 16:9, 5056 × 3392 at 3:2 and 4096 square at 1:1.
5. **Check.** Claude checks text, drips, pairs and small details at full size and shows Josh the crops. Josh gives the yes.
6. **Finish.** pipeline/finish.py automates what Josh did by hand on Deluge: place the untouched 4K render at 1:1 on a 6704 square canvas, extend the backdrop, isolate the device, recolor the backdrop until the glow behind the device matches the track swatch, export a JPG of about 12 MB. Deluge v1 went from 5056 × 3392 to 6704 square this way in Photoshop with Generative Expand (measured Oct 28 2026), and the script matches its backdrop color within deltaE 2.2. Photoshop stays available for last small fixes.
7. **Place.** The master goes into the Photo layer of the track's Cover, Post and Canvas boards in Figma. Exports are preset on every board.

Upscaling a 1264 px render does not work. Topaz Gigapixel invented grille and panel detail in the Oct 18 2026 test.

## Series lock · set on Spice round 1, Oct 18 2026
Figma's generator can't take Deluge as a reference image, so consistency comes from these blocks, pasted word for word into every track's prompt. Only the device and the spill change.

- **Scene** · real 1990 mail order catalog photo on medium format film, 80mm lens, fine grain, muted print color. Straight on at the device's own height. Seamless sweep in the track color with no horizon and no studio gear. Soft diffused light from the upper left, from a source well outside the frame, soft contact shadow only. Never name a softbox in the prompt. Naming it put the light in frame on four of six Determinator frames, and describing the light without the word cleared all four reruns (Oct 19 2026). Brighter glow behind the device and on the floor, falling to a deeper shade of the ground in the top corners. Device fills about half the frame height
- **Camera exception** · a device that has to show its top, like a turntable platter, gets a front view raised about 25 degrees, still squared up to the front. The generator ignored low camera requests on Bopkins, then called Danish (Oct 19 2026)
- **Frame** · every object, accessories and pool included, sits inside the frame with clear backdrop at every edge. Nothing cropped (added Oct 19 2026)
- **Dough, firm · default from Oct 19 2026** · firm, freshly kneaded raw bread dough that holds its shape, one cohesive mass, pale oatmeal beige like raw pizza dough, never pink and never meaty. Satin matte skin with fine stretch lines and soft folds, no holes, no lace, no webbing. Where it meets the floor it stays thick and rounded. No pool, no puddle, nothing runny, wet or glossy. Shaped only by gravity. Josh asked for nothing runny on Suavecita, and this wording removed every pool
- **Dough, poured · used on Deluge, Spice and Bopkins** · one cohesive mass of raw kneaded bread dough, pale oatmeal beige like raw pizza dough, never pink and never meaty. Satin matte skin with fine stretch lines, no holes, no lace, no webbing. One thick heavy lobe. The pool is a thick soft edged puddle with a dull satin surface, not liquid and not glossy. Shaped only by gravity
- **Real proportions** · state the size relationship that makes the device believable, for example a Walkman body only slightly larger than a standard audio cassette with a door the full size of one. Without it the generator draws toy sized parts
- **Never ask for** a pink cast or gluten strands. On Spice pass A those words turned the dough into lace and raw meat
- **Color** · the eye judges dough against its ground, so on warm grounds the dough can measure a few degrees yellower than Deluge and still read the same. The final match happens by eye in Photoshop
- **Spill side** · the dough's weight sits at the left third where it can, so the covers read as a set. It sets where the weight goes, never the shape
- **Silhouette · set by Josh Oct 19 2026** · every track gets its own dough outline. Spice through Traycee all ended in a lobe sagging out the left into a mound, and the covers started to rhyme. Describe a specific shape in each prompt (a brick, a ball, a heap, a braid) instead of reusing the pour language

## Locked decisions
- **Album cover** · translucent tangerine Walkman, tape door hanging open, a large wad of dough stuffed in where the cassette goes. Grey placeholder ground for now, v1 catalog ad copy on the canvas
- **Store master** · distributors only accept the band name and album title as text, so the cover sent to Spotify drops the ad copy. Same rule for any track cover released as a single
- **Naming** · never abbreviate the album name. The band abbreviates to CBDB, so catalog numbers run CBDB 00 for the album and CBDB 01 to CBDB 09 for tracks
- **Dough look** · too big to fit, sagging out the side, thick slow drips that are never stringy. One deck clearly dominates the spill. Overflow and main drip land near a rule of thirds line
- **Dough is lifeless** · gravity is the only force on it. It never rises, swells, reaches, crawls, pushes a door open or gets ejected. Drips cling to the device. No accidental faces, no matched pairs of wads, highlights or drips that read as eyes or legs. Canvas loops are gravity only and never play in reverse
- **Format** · full bleed everywhere, one surface per layout
- **Palette** · nine chroma matched track colors, all at the 500 step. Wheel order Blueberry, Butter, Cherry, Bondi, Bubblegum, Lime, Grape, Tangerine, Mint, chosen so every neighbor has the highest contrast. Dough #E9D3A8 is reserved for the dough itself. Paper #F5EEDC, Ink #2A2522
- **Color order** · wheel order whenever the nine appear as a set. In a 3 by 3 grid, wrap it clockwise around the edge with Mint in the middle. When tracks must run 01 to 09, each color gets its own tile with a paper gutter or ink rule between, never a shared edge
- **Color roles** · Surface, Ink, Primary brand (Bondi and Tangerine) and Secondary album, with 100 to 900 ramps. Only 500 steps on covers. Ink type works on all nine grounds, bold 18 px and up on Cherry and Grape
- **Type** · Anton for titles, Archivo for band name and fine print, Share Tech Mono for model numbers and runtimes. Free Google Fonts only
- **Track covers** · catalog layout set by Josh on the Deluge cover Oct 18 2026. Meta row and rule, big title with the subhead tight under it, device photo filling about 85 percent of the width and sitting on the footer. Fresh Batch sticker tilted 18 degrees clockwise at the upper right, overlapping the device. Footer is runtime left, band name and legal line centered, spec list right. No features column, no spec rule, halftone and paper textures off for now. Sticker ring is Bondi on warm grounds, Tangerine on cool grounds
- **Instagram** · native 4:5 post for every track, same layout as the cover scaled to 720 wide with the spec list reading Out Now. The album post is the cover shown as a 7 inch single on paper. The 3:4 profile grid trims the sides, so type stays inside the crop
- **Production** · image generation, no photoshoot (decided Oct 18 2026). See the device photo workflow above
- **Device photo recipe** · name the device parts, add analog knobs and buttons, and a small glowing red power light where a real one would sit (a lit screen counts). No people, hands, logos or brand names. Exploration renders say no readable text, the 4K prompt supplies the exact real label words. Scene and dough come from the series lock
- **Canva** · any image Claude generates in Canva moves straight into the Titus Tests folder
- **Rollout** · Spotify first, then Instagram, then other platforms once the distributor is chosen

## Track list · best match colors as of Oct 19 2026
1. Deluge · Silver dual deck boombox · Bondi #65B8E5 · Deluge v1 final (drips retouched, square expand, color corrected to Bondi). In the repo and Drive Masters, Figma placement is Claude Code's first job
2. Spice · Yellow sports Walkman · Butter #ECCE7B · F2 approved Oct 19 2026 after five rounds. Front door hinged on the right and pinched on the dough, spill at the left third, yellow headphones with orange pads on the right. Queued for 4K
3. Bopkins (was Danish) · Turntable · Bubblegum #E99CC2 · G1 approved Oct 19 2026 in round 1. Silver deck, flat record shaped pile with the spindle through it, raised front camera, spill at the left third. Queued for 4K
4. Suavecita · Virtual pet in a Bubblegum shell · Cherry #C77171 · I4 approved Oct 19 2026 in round 2. Clear pink shell with the circuit board showing, leaning back in a firm dough nest, no pool. Original pixel pet on the screen, never a real character, no lettering on the shell. Queued for 4K
5. Traycee · Tube monitor and tower PC · Mint #73D2AB · Moved to node 81:2 on Oct 28 2026 (K4 was the Oct 19 pick). Beige 1996 tower and CRT with two small speakers, no keyboard. A heavy lobe over the open CD tray falling to a big rounded mound on the floor. First 4K run done Oct 28 2026, tight 16:9 crop re-run next
6. Determinator · TV VCR combo · Blueberry #6C8DCE · round 1 started Oct 19 2026. Dough jammed in the VHS slot, out the left end to a firm mound. Screen glows video blue. L6 (charcoal 19 inch) carried into a shape set Oct 19 2026 after Josh flagged the silhouettes rhyming. Pick M1 (dough brick shaped like a VHS tape, half in the slot), runner up M5 (the whole batch heaped on the floor, one fold crammed in)
7. Boombap (was Midnight Honey) · Clock radio with dough plopped on top · Tangerine #DE9F65
8. Mancub · Classic grey handheld game console, no logos · Lime #82A967
9. Show Me Your Love · Talkboy with its logo changed to Doughboy · Grape #8E74B7

Watch outs · Bopkins into Suavecita is the one weak border in track order (18.7), so it always gets a gutter. On the 1:1 cover the upper right sticker clips long titles (Determinator, Show Me Your Love). The softbox edge kept sneaking into the top left corner until the series lock stopped naming it (Oct 19 2026). Still check every frame for it.

## Never
- Hands, people or real brand logos
- Callout or parts diagrams
- Paper bands or split panels
- Dough color as a fill or type
- Clean vectors, screen neon or filter presets
- Dough that rises, reaches or reads alive

## Open
- Album cover ground color
- Runtimes for each track
- Which tracks release early as singles
- Distributor
- Vinyl go or no go
