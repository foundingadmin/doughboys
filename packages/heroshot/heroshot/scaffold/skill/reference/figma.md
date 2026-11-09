# Figma · review boards and placing a master

Every image the approver reviews is assembled on a board in Figma, never only in the repo or in chat. One board per review, options side by side, matched crops at native pixels, a pass or fail note under each.

Set in heroshot.json `figma`: `file_key`, `review_page_id`, and `sections` (stage name to section node id, for example `{"Exploration": "214:12"}`) if the review page is split by stage. Look pages and sections up by id, never by name. Read the page first: people rearrange it by hand, and a board dropped by an old layout script can duplicate their sections.

Load the figma-use skill before any `use_figma` call, and call `create_session` with the file key first.

## Building a review board

1. Make the images in `work/<slug>/figma/`: JPG under 10 MB each. Full renders downscaled to 4096 wide, check crops cut from the full render at native pixels, the same boxes for every option.
2. Copy `review_board.js` (next to this file), fill in `BOARD`, `ROWS` and `PLACE`, run it as one `use_figma` call. It returns `slots`, one empty rectangle per image.
3. `upload_assets` with `count` and `nodeIds` in slot order, then POST each file to its URL: `curl -sS -X POST -H "Content-Type: image/jpeg" --data-binary @FILE "SUBMIT_URL"`.
4. `get_screenshot` the board, save it to `<dir>/review/<slug>/board-<id>.png`, look at it, give the approver `https://www.figma.com/design/<file_key>?node-id=<id with - for :>`.
5. Record the board id in heroshot.json under the item's `review_boards`.

Name every board starting with the item id, so a column per item stays sortable.

## Placing a finished master

1. `heroshot finish` already wrote the 4096 upload copy (`work/<slug>/<slug>-final-v1-4096.jpg`). Upload it with `upload_assets` without a target node and keep the image hash and `placedOnNodeId` (a temporary frame to delete afterward).
2. Put it in the layout as an image fill on a rectangle. If the layout is a component with a slot or a photo frame, append the rectangle inside it so it can be moved and scaled without detaching.
3. For 4:5 and 9:16 boards use the item's `framing` from heroshot.json: `[[w, 0, tx], [0, 1, 0]]` means show a `w` wide slice starting `tx` from the left. As a free layer in a square frame of size `S`, set the image to `S × S` and `x = -tx × S`.
4. Screenshot the result and look at it: subject clear of type and stickers, ground continuous edge to edge. Wide subjects clip on 9:16, say so.

## Gotchas

- Every `use_figma` script is atomic. One error rolls back the whole script.
- The page resets every call. Start each script with `setCurrentPageAsync`.
- Load fonts before touching any text.
- Figma rotation is counterclockwise positive.
