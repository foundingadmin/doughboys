# Figma · how the file is built and how to place a finished photo

File key `lcNDgyPE02C9Ldw8n2THee`. Built Oct 29 2026 from the Claude design canvas, which is now retired. Figma is the source of truth.

## Structure

**Variables** (Kit page)
- `Primitives` `VariableCollectionId:114:5` · nine track ramps (blueberry, butter, cherry, bondi, bubblegum, lime, grape, tangerine, mint) at 100 to 900, ink, paper, dough, placeholder. Hidden from pickers.
- `Semantic` `VariableCollectionId:114:71` · surface, ink, brand/blue (Bondi), brand/orange (Tangerine), album/* (the 500 steps).
- `Track` `VariableCollectionId:114:90` · one mode per track. Ground, ring, ink, tint, number, title, catalog, subhead, device, dough note, motion, runtime, title size, position. Changing a value here changes every board for that track.

**Components** (Kit page)
- `Track Art` component set `116:104` with variants Format = Cover 1:1 `116:2`, Post 4:5 `116:47`, Canvas 9:16 `116:89`.
  Properties: `Show placeholder#116:0`, `Print pass#116:4`, `Player zones#116:8`.
- `Album Cover` set `117:87` (Ad `117:32`, Store `117:76`), property `Show placeholder#117:0`. `Album Post 4:5` `117:88`.
- Parts: Spec row `115:21`, Runtime `115:32`, Fresh Batch sticker `115:39`, Nine Tracks sticker `117:70`.

**Album Art page** `114:4`
- Readme frame `118:2`, album section `118:9`, then one section per track. Each section pins its Track mode, so the three boards inside it pick up that track's colors and copy.
- Instance ids per track are in `tracks.json` under `figma`.

## Placing a finished master

1. Make the Figma copy: the master downscaled to 4096 square, JPG quality 95, in `work/` (uploads cap at 10 MB and Figma stores 4096 max anyway). Upload it with the Figma `upload_assets` tool, without a target node, and keep the returned image hash and `placedOnNodeId`. The upload goes from this container to `mcp.figma.com`, so that host must be allowed.

```bash
python3 -c "from PIL import Image; Image.open('MASTER.jpg').resize((4096,4096), Image.LANCZOS).save('work/NN-track/figma4096.jpg', quality=95, subsampling=0)"
```

```bash
curl -sS -X POST -F "file=@work/NN-track/figma4096.jpg;type=image/jpeg" "SUBMIT_URL"
```
2. Get the Post and Canvas crop: `python3 pipeline/framing.py MASTER_alpha_small.npy` (finish.py writes that file next to the master). It prints both transforms.
3. Run one `use_figma` call on the Album Art page:

```js
const page = figma.root.children.find(p => p.id === "114:4");
await figma.setCurrentPageAsync(page);
const HASH = "<image hash>";
const boards = {
  cover:  { id: "<cover instance id>",  t: [[1, 0, 0], [0, 1, 0]] },
  post:   { id: "<post instance id>",   t: [[0.8, 0, POST_TX], [0, 1, 0]] },
  canvas: { id: "<canvas instance id>", t: [[0.5625, 0, CANVAS_TX], [0, 1, 0]] },
};
const done = {};
for (const [k, b] of Object.entries(boards)) {
  const inst = await figma.getNodeByIdAsync(b.id);
  const photo = inst.findOne(n => n.name === "Photo");
  photo.fills = [{ type: "IMAGE", imageHash: HASH, scaleMode: k === "cover" ? "FILL" : "CROP", imageTransform: b.t }];
  inst.setProperties({ "Show placeholder#116:0": false });
  done[k] = photo.id;
}
// the upload dropped a temporary frame on the page, remove it
const tmp = await figma.getNodeByIdAsync("<placedOnNodeId>");
if (tmp && tmp.parent && tmp.parent.type === "PAGE") tmp.remove();
return done;
```

4. `get_screenshot` the track's section (all three boards in one image) and save it to `the-first-batch/review/NN-track/figma-boards-v1.png`. Look at it: device not clipped by the sticker or the type, ground continuous from photo edge to board edge.
5. Record the hash and transforms in tracks.json, and update art-direction.md (see CLAUDE.md, Keeping the docs current).

## Review boards

Josh reviews every image in Figma (set Oct 29 2026). Boards live on the Review page `128:77`, one per review, stacked newest at the bottom.

1. Make the images in `work/NN-track/figma/`. Full frames downscaled to 4096 wide, check crops cut from the full render at native pixels, the same boxes for every option. JPG, under 10 MB each.
2. Copy `pipeline/figma_review_board.js`, fill in `BOARD` and `ROWS`, run it as one `use_figma` call. It returns `slots` with an empty rectangle per file.
3. `upload_assets` with `count` and `nodeIds` in slot order, then POST each file to its URL. Each image lands in its slot.
4. `get_screenshot` the board, look at it, give Josh the link `https://www.figma.com/design/lcNDgyPE02C9Ldw8n2THee?node-id=<board id with - for :>`.
5. Record the board id in tracks.json under the track's `review_boards`.

## Gotchas learned building it

- Every `use_figma` script is atomic. One error rolls back the whole script, so a failed call changed nothing.
- The page resets every call. Start each script with `setCurrentPageAsync`.
- Load fonts before touching any text, even `textAutoResize`. Fonts: Anton Regular, Archivo (Regular, Bold), Share Tech Mono Regular.
- Drop shadows need `blendMode: "NORMAL"` and `showShadowBehindNode: false`.
- Figma rotation is counterclockwise positive. The sticker's 18 degree clockwise tilt is `-18`.
- Album cover Show placeholder is `#117:0`, not `#116:0`.
