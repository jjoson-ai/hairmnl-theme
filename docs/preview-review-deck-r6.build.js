const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Final Page Check";

// ---- palette ----
const INK = "1F2933", TERRA = "B85042", WHITE = "FFFFFF", MUTED = "5A6470",
      LIGHT = "F3F4F6", ICE = "CAD3DC", GREEN = "2E7D5B", AMBER = "C77D34", GRAY = "8A8F98";
const HF = "Georgia", BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com";
const NF = "?preview_theme_id=141655801955&_fd=0&_sc=1";
const L = (path) => STORE + path + NF;
const PDP = "/products/davines-naturaltech-purifying-shampoo-for-scalp-with-oily-or-dry-dandruff";
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function footer(slide, n) {
  slide.addText("HairMNL · Pipeline 8 — pages to check before go-live", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "left", margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(slide, label, title) {
  slide.addText(label.toUpperCase(), { x: 0.5, y: 0.4, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.5, y: 0.72, w: 12.3, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: INK, margin: 0 });
}
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle", align: "left" } });
const tc = (t, opts = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: opts.fill || WHITE }, ...opts } });
const wasCell = (t) => ({ text: t, options: { fontSize: 10, fontFace: BF, italic: true, color: TERRA, valign: "middle", fill: { color: "FBF3F1" } } });

// ============ SLIDE 1 — TITLE + HOW TO OPEN ============
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · FINAL CHECK", { x: 0.9, y: 0.95, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("A few pages to verify before we go live", { x: 0.9, y: 1.45, w: 11.8, h: 1.0, fontFace: HF, fontSize: 38, bold: true, color: WHITE, margin: 0 });
s.addText("These are the spots that gave us trouble in earlier rounds — they're fixed now. Please confirm each one on a phone. The items flagged in red are the ones that were buggy before, so give those an extra look.",
  { x: 0.9, y: 2.65, w: 11.4, h: 1.0, fontFace: BF, fontSize: 15, color: ICE, margin: 0, lineSpacingMultiple: 1.12 });

// how to open — essential
s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 3.95, w: 11.5, h: 1.05, fill: { color: "3A2E2C" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "📱 Open each link directly on your phone ", options: { bold: true, color: WHITE } },
  { text: "(tap it, or paste it into a new tab). Don't browse from one page to the next — that bounces you to the live site, where the new features won't show.", options: { color: ICE } },
], { x: 1.15, y: 4.05, w: 11.0, h: 0.85, fontFace: BF, fontSize: 13, valign: "middle", margin: 0, lineSpacingMultiple: 1.1 });

// the links
s.addText("The three pages:", { x: 0.9, y: 5.25, w: 11, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: GRAY, margin: 0 });
s.addText([
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Collection (Products)", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "A product page", options: { hyperlink: { url: L(PDP) }, color: WHITE, bold: true } },
], { x: 0.9, y: 5.6, w: 11.6, h: 0.5, fontFace: BF, fontSize: 14, margin: 0 });

// ============ SLIDE 2 — PRODUCT PAGE ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Product page", "Open a product page, then check:");
let rows = [
  [hcell("What to check"), hcell("What you should see now"), hcell("⚠ Was buggy before")],
  [tc("Quick Buy on the suggestion cards", { bold: true }),
   tc("Tap the round cart icon → a size picker pops up → tap a size → it adds to the cart without leaving the page."),
   wasCell("Tapping jumped to the product page; the picker didn't open.")],
  [tc("Sticky Add to Cart bar", { bold: true }),
   tc("Scroll down — a bar slides in (top on desktop, bottom on mobile): size + qty + ADD TO CART on ONE row, button fully visible."),
   wasCell("Didn't appear at all / wrapped to two rows / button cut off.")],
  [tc("Button colours", { bold: true }),
   tc("ADD TO CART is dark; the selected size pill is light grey."),
   wasCell("Wrong colours.")],
  [tc("“Complete Your Routine” cards", { bold: true }),
   tc("All cards use the same image size; titles and prices line up in a neat row."),
   wasCell("Cards misaligned / different image sizes.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.6, w: 12.33, colW: [3.4, 5.5, 3.43],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.0, 1.15, 0.6, 0.85], margin: [4, 6, 4, 6],
});
s.addText([
  { text: "Open: ", options: { color: MUTED } },
  { text: "this product page", options: { hyperlink: { url: L(PDP) }, color: TERRA, bold: true } },
], { x: 0.5, y: 6.55, w: 12, h: 0.35, fontFace: BF, fontSize: 12, margin: 0 });
footer(s, 2);

// ============ SLIDE 3 — COLLECTION / CART / HOME ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Collection, cart & home", "Then check these:");
rows = [
  [hcell("Where"), hcell("What you should see now"), hcell("⚠ Was buggy before")],
  [tc("Collection / Best Sellers — Quick Buy icon", { bold: true }),
   tc("A small, subtle cart icon at the top-right of each card; tap it → size picker → adds to cart."),
   wasCell("Icon was too big; tapping went to the product page.")],
  [tc("Cart drawer — suggestions", { bold: true }),
   tc("Suggestion cards are aligned, and products already in your cart do NOT appear in the suggestions."),
   wasCell("Cards misaligned; suggestions showed items already in the cart.")],
  [tc("Mobile home — hero banner", { bold: true }),
   tc("On a phone, the hero banner fills the screen edge-to-edge — no white gaps on the left/right."),
   wasCell("White side-gaps; banner not full-width on mobile.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.6, w: 12.33, colW: [3.4, 5.5, 3.43],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.0, 1.0, 1.0], margin: [4, 6, 4, 6],
});
s.addText([
  { text: "Open: ", options: { color: MUTED } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: TERRA, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Home (for the banner)", options: { hyperlink: { url: L("/") }, color: TERRA, bold: true } },
  { text: "   ·   cart: add an item, then open the cart drawer.", options: { color: MUTED } },
], { x: 0.5, y: 5.3, w: 12.3, h: 0.4, fontFace: BF, fontSize: 12, margin: 0 });
footer(s, 3);

// ============ SLIDE 4 — CLOSING ============
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("THAT'S THE LIST", { x: 0.9, y: 2.0, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("If these all check out, we're clear to go live.", { x: 0.9, y: 2.5, w: 11.7, h: 1.3, fontFace: HF, fontSize: 34, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Tick off each item on a phone (remember: open the links directly, don't click through). ", options: { color: ICE } },
  { text: "If anything still looks off, screenshot it and note which page + device — and we'll jump on it before publishing.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 3.95, w: 11.3, h: 1.4, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
s.addText([
  { text: "Pages:  ", options: { color: GRAY } },
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Product page", options: { hyperlink: { url: L(PDP) }, color: WHITE, bold: true } },
], { x: 0.9, y: 6.4, w: 11.6, h: 0.3, fontFace: BF, fontSize: 12, margin: 0 });

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Final-Page-Check.pptx" }).then(f => console.log("WROTE", f));
