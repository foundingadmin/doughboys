// Review board for the Figma Review page. Paste into one use_figma call after
// editing BOARD and ROWS. Each tile with a `file` gets an empty slot; the call
// returns { slots: [{ file, id }] }, then upload_assets with nodeIds in that
// order and POST each file to its URL. A tile with `hash` reuses an image
// already in the file (Deluge v1 is 1419471e018a654ff8a9e9a5e8ed364834169f0f).
// Crops go up at native render pixels so Josh can zoom to 100 percent.

const BOARD = {
  name: "CBDB NN Track · what is being reviewed · Mon D YYYY",
  title: "TRACK · WHAT IS BEING REVIEWED",
  meta: "CBDB NN · Mon D YYYY · source, crop, model, size",
  ask: "Your call: the one decision Josh needs to make, and the recommendation.",
};
// [rowTitle, [label, note, file, w, h, hash?], [label, note, file, w, h, hash?]]
// A one tile row is fine: [rowTitle, [label, note, file, w, h]]
const ROWS = [
  ["Full frame",
    ["A · label", "What passed and what failed.", "a-full.jpg", 4096, 2747],
    ["B · label", "What passed and what failed.", "b-full.jpg", 4096, 2747]],
];

let page = figma.root.children.find(p => p.name === "Review");
if (!page) {
  page = figma.createPage(); page.name = "Review";
  figma.root.insertChild(figma.root.children.findIndex(p => p.id === "114:4") + 1, page);
}
await figma.setCurrentPageAsync(page);
await Promise.all([
  figma.loadFontAsync({ family: "Anton", style: "Regular" }),
  figma.loadFontAsync({ family: "Archivo", style: "Regular" }),
  figma.loadFontAsync({ family: "Archivo", style: "Bold" }),
  figma.loadFontAsync({ family: "Share Tech Mono", style: "Regular" }),
]);
// Semantic surface/page, surface/panel, ink/primary, ink/muted
const [vPage, vPanel, vInk, vMuted] = await Promise.all(["VariableID:114:72", "VariableID:114:73", "VariableID:114:75", "VariableID:114:77"].map(id => figma.variables.getVariableByIdAsync(id)));
const paint = v => figma.variables.setBoundVariableForPaint({ type: "SOLID", color: { r: 0, g: 0, b: 0 } }, "color", v);
const text = (s, family, style, size, v, width) => {
  const t = figma.createText();
  t.fontName = { family, style }; t.fontSize = size; t.characters = s; t.fills = [paint(v)];
  if (width) { t.textAutoResize = "HEIGHT"; t.resize(width, t.height); }
  return t;
};
// New boards stack below the existing ones, newest at the bottom
let maxY = 0;
for (const c of page.children) maxY = Math.max(maxY, c.y + c.height);

const COL = 1600, GAP = 48;
const board = figma.createAutoLayout("VERTICAL", { name: BOARD.name, itemSpacing: 96, paddingLeft: 96, paddingRight: 96, paddingTop: 96, paddingBottom: 96 });
board.fills = [paint(vPage)];
board.x = 0; board.y = maxY ? maxY + 400 : 0;
const head = figma.createAutoLayout("VERTICAL", { name: "Header", itemSpacing: 16 });
board.appendChild(head);
head.appendChild(text(BOARD.title, "Anton", "Regular", 120, vInk));
head.appendChild(text(BOARD.meta, "Share Tech Mono", "Regular", 32, vMuted));
head.appendChild(text(BOARD.ask, "Archivo", "Bold", 40, vInk, COL * 2 + GAP));

const slots = [];
const tile = (parent, [label, note, file, w, h, hash]) => {
  const t = figma.createAutoLayout("VERTICAL", { name: label, itemSpacing: 16 });
  parent.appendChild(t);
  t.appendChild(text(label, "Archivo", "Bold", 32, vInk));
  const r = figma.createRectangle(); r.name = file; r.resize(COL, Math.round(COL * h / w));
  r.fills = hash ? [{ type: "IMAGE", imageHash: hash, scaleMode: "FILL" }] : [paint(vPanel)];
  t.appendChild(r);
  t.appendChild(text(note, "Archivo", "Regular", 28, vMuted, COL));
  if (!hash) slots.push({ file, id: r.id });
};
for (const [title, ...tiles] of ROWS) {
  const s = figma.createAutoLayout("VERTICAL", { name: title, itemSpacing: 24 });
  board.appendChild(s);
  s.appendChild(text(title.toUpperCase(), "Share Tech Mono", "Regular", 36, vInk));
  const r = figma.createAutoLayout("HORIZONTAL", { name: title + " · pair", itemSpacing: GAP });
  s.appendChild(r);
  for (const t of tiles) tile(r, t);
}
return { pageId: page.id, boardId: board.id, size: [board.width, board.height], slots };
