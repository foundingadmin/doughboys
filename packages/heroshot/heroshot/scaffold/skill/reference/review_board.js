// heroshot review board. Paste into one use_figma call after filling BOARD, ROWS and PLACE.
// Each tile with a file gets an empty slot. The call returns { slots: [{ file, id }] }, then
// upload_assets with nodeIds in that order and POST each file to its URL.
// A tile with `hash` reuses an image already in the file (an earlier approved master, for comparison).

const BOARD = {
  name: "ID Title · what is being reviewed · Mon D YYYY",
  title: "TITLE · WHAT IS BEING REVIEWED",
  meta: "ID · Mon D YYYY · model · size · swatch",
  ask: "Your call: the one decision the approver needs to make, and the recommendation.",
};
// [rowTitle, [label, note, file, w, h, hash?], ...]  any number of tiles per row
const ROWS = [
  ["Round 1",
    ["1 · label", "What works. What is off.", "r1-1.jpg", 1024, 1024],
    ["2 · label", "What works. What is off.", "r1-2.jpg", 1024, 1024],
    ["3 · label", "What works. What is off.", "r1-3.jpg", 1024, 1024]],
];
const PLACE = { pageId: "REVIEW_PAGE_ID", sectionId: null, below: null };  // sectionId to drop it in a section, below = a board id to stack under
const COL = 1200, GAP = 48;
const INK = { r: 0.13, g: 0.13, b: 0.13 }, MUTED = { r: 0.42, g: 0.42, b: 0.42 }, PAPER = { r: 1, g: 1, b: 1 }, PANEL = { r: 0.93, g: 0.93, b: 0.93 };
const FONT = { family: "Inter", regular: "Regular", bold: "Bold" };

const page = await figma.getNodeByIdAsync(PLACE.pageId);
await figma.setCurrentPageAsync(page);
await Promise.all([figma.loadFontAsync({ family: FONT.family, style: FONT.regular }), figma.loadFontAsync({ family: FONT.family, style: FONT.bold })]);
const solid = c => [{ type: "SOLID", color: c }];
const text = (s, bold, size, color, width) => {
  const t = figma.createText();
  t.fontName = { family: FONT.family, style: bold ? FONT.bold : FONT.regular }; t.fontSize = size; t.characters = s; t.fills = solid(color);
  if (width) { t.textAutoResize = "HEIGHT"; t.resize(width, t.height); }
  return t;
};
const widest = Math.max(...ROWS.map(r => r.length - 1));
const board = figma.createAutoLayout("VERTICAL", { name: BOARD.name, itemSpacing: 96, paddingLeft: 96, paddingRight: 96, paddingTop: 96, paddingBottom: 96 });
board.fills = solid(PAPER);
const head = figma.createAutoLayout("VERTICAL", { name: "Header", itemSpacing: 16 });
board.appendChild(head);
head.appendChild(text(BOARD.title, true, 96, INK));
head.appendChild(text(BOARD.meta, false, 28, MUTED, COL * widest + GAP * (widest - 1)));
head.appendChild(text(BOARD.ask, true, 40, INK, COL * widest + GAP * (widest - 1)));
const slots = [];
for (const [title, ...tiles] of ROWS) {
  const s = figma.createAutoLayout("VERTICAL", { name: title, itemSpacing: 24 });
  board.appendChild(s);
  s.appendChild(text(title.toUpperCase(), false, 36, INK));
  const row = figma.createAutoLayout("HORIZONTAL", { name: title + " · row", itemSpacing: GAP });
  s.appendChild(row);
  for (const [label, note, file, w, h, hash] of tiles) {
    const t = figma.createAutoLayout("VERTICAL", { name: label, itemSpacing: 16 });
    row.appendChild(t);
    t.appendChild(text(label, true, 32, INK));
    const r = figma.createRectangle(); r.name = file; r.resize(COL, Math.round(COL * h / w));
    r.fills = hash ? [{ type: "IMAGE", imageHash: hash, scaleMode: "FILL" }] : solid(PANEL);
    t.appendChild(r);
    t.appendChild(text(note, false, 28, MUTED, COL));
    if (!hash) slots.push({ file, id: r.id });
  }
}
const parent = PLACE.sectionId ? await figma.getNodeByIdAsync(PLACE.sectionId) : page;
parent.appendChild(board);
if (PLACE.below) { const b = await figma.getNodeByIdAsync(PLACE.below); board.x = b.x; board.y = b.y + b.height + 400; }
else { const kids = parent.children.filter(n => n !== board); board.x = parent.type === "SECTION" ? 600 : (kids.length ? Math.max(...kids.map(n => n.x + n.width)) + 400 : 0); board.y = parent.type === "SECTION" ? 600 : 0; }
return { boardId: board.id, size: [board.width, board.height], slots };
