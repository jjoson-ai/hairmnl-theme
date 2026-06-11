const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Preview Review, Round 3";

// ---- palette ----
const INK   = "1F2933";
const TERRA = "B85042";
const WHITE = "FFFFFF";
const MUTED = "5A6470";
const LIGHT = "F3F4F6";
const ICE   = "CAD3DC";
const GREEN = "2E7D5B";
const AMBER = "C77D34";
const GRAY  = "8A8F98";

const HF = "Georgia";
const BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com";
const PID = "?preview_theme_id=141168312419";
const L = (path) => STORE + path + PID;

const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function footer(slide, n) {
  slide.addText("HairMNL · Pipeline 8 — preview review · round 3 (11 Jun comments)", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "left", margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(slide, label, title) {
  slide.addText(label.toUpperCase(), { x: 0.5, y: 0.4, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.5, y: 0.72, w: 12.3, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: INK, margin: 0 });
}
function pill(text, color) {
  return { text, options: { fill: { color }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 10, fontFace: BF } };
}
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle", align: "left" } });
const tc = (t, opts = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: opts.fill || WHITE }, ...opts } });

// =====================================================================
// SLIDE 1 — TITLE
// =====================================================================
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · STORE PREVIEW · ROUND 3", { x: 0.9, y: 1.45, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Your June 11 comments — all 14 addressed", { x: 0.9, y: 1.95, w: 11.8, h: 1.3, fontFace: HF, fontSize: 40, bold: true, color: WHITE, margin: 0 });
s.addText("Including the Quick Buy redesign you sketched, the recommendation-card matching, the sold-out/freebie clean-up — and the mobile banner, which is now fixed on the LIVE site as well.",
  { x: 0.9, y: 3.3, w: 11, h: 0.95, fontFace: BF, fontSize: 16, color: ICE, margin: 0 });
s.addText([
  { text: "Open the preview store:  ", options: { color: ICE } },
  { text: "click here", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "   — fresh window + hard refresh, please (cached tabs showed you stale pages last round).", options: { color: GRAY } },
], { x: 0.9, y: 4.7, w: 11.6, h: 0.5, fontFace: BF, fontSize: 12, margin: 0 });

// =====================================================================
// SLIDE 2 — SUMMARY
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Where things stand", "Everything from June 11 is in");

const stats = [
  { n: "14", t: "of 14 comments addressed", d: "every slide in your June-11 review", c: GREEN },
  { n: "LIVE", t: "mobile banner fixed on the live site", d: "the one change you asked us to ship to the current store — done", c: TERRA },
  { n: "✕", t: "no more bad recommendations", d: "sold-out, freebie/promo and salon-only items are filtered out", c: INK },
  { n: "1", t: "step left", d: "your fresh-preview look, then sign-off", c: AMBER },
];
const sx = 0.5, sy = 1.7, sw = 3.55, sh = 1.95, gap = 0.32;
stats.forEach((it, i) => {
  const x = sx + (i % 2) * (sw + gap);
  const y = sy + Math.floor(i / 2) * (sh + gap);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: sw, h: sh, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.1, h: sh, fill: { color: it.c } });
  s.addText(it.n, { x: x + 0.25, y: y + 0.16, w: sw - 0.5, h: 0.8, fontFace: HF, fontSize: 40, bold: true, color: it.c, margin: 0, align: "left" });
  s.addText(it.t, { x: x + 0.27, y: y + 0.98, w: sw - 0.5, h: 0.45, fontFace: BF, fontSize: 13, bold: true, color: INK, margin: 0 });
  s.addText(it.d, { x: x + 0.27, y: y + 1.42, w: sw - 0.45, h: 0.5, fontFace: BF, fontSize: 10.5, color: MUTED, margin: 0 });
});

s.addShape(pres.shapes.RECTANGLE, { x: 8.35, y: 1.7, w: 4.5, h: 4.22, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText("Two timing notes", { x: 8.55, y: 1.85, w: 4.1, h: 0.35, fontFace: BF, fontSize: 13, bold: true, color: TERRA, margin: 0 });
s.addText([
  { text: "The live banner fix can take up to ~30 minutes to show for everyone (page caching). Hard-refresh if you check right away.", options: { color: MUTED, breakLine: true } },
  { text: "\nThe recommendation clean-up works in two layers: the on-page filter is active on the preview NOW; the deeper engine-side filter kicks in on its next scheduled refresh. If one stray item slips through this week, it will clear on its own.", options: { color: MUTED } },
], { x: 8.55, y: 2.25, w: 4.1, h: 3.5, fontFace: BF, fontSize: 11, valign: "top", margin: 0, lineSpacingMultiple: 1.1 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 6.1, w: 12.33, h: 0.8, fill: { color: INK } });
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 6.1, w: 0.1, h: 0.8, fill: { color: TERRA } });
s.addText([
  { text: "In short:  ", options: { bold: true, color: TERRA } },
  { text: "the bar behaves, Quick Buy looks like the app's icon (variant picker included), every slider matches the site's cards, the banner is full-width on live mobile, and the recs are clean. One fresh look and we ship.", options: { color: ICE } },
], { x: 0.8, y: 6.15, w: 11.8, h: 0.7, fontFace: BF, fontSize: 12, valign: "middle", margin: 0 });
footer(s, 2);

// =====================================================================
// SLIDE 3 — STICKY BAR
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Your comments, part 1", "Sticky bar");

const rows3 = [
  [hcell("You asked"), hcell("Status"), hcell("What it does now")],
  [tc("Add to Cart was jumping to another page — it should only add to cart"),
   pill("FIXED", GREEN),
   tc("The bar's button now adds to the cart in place and opens the cart drawer. You stay on the product page.")],
  [tc("Mobile: extend the ADD TO CART button to fill the bar"),
   pill("FIXED", GREEN),
   tc("Price and quantity sit compact on the left; the button takes the rest of the bar, like your mock.")],
  [tc("Desktop: replace the brand name with the star rating + review count"),
   pill("FIXED", GREEN),
   tc("The bar now shows ⭐ stars and the review count under the product title — same rating source as the product cards.")],
  [tc("Hide the bar when the cart drawer is open (it covered the drawer / checkout button)"),
   pill("FIXED", GREEN),
   tc("The bar disappears the moment the drawer opens and returns when it closes — tested both ways.")],
];
s.addTable(rows3, {
  x: 0.5, y: 1.65, w: 12.33, colW: [4.5, 1.3, 6.53],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 0.9, 0.85, 0.9, 0.9], margin: [3, 5, 3, 5],
});
footer(s, 3);

// =====================================================================
// SLIDE 4 — QUICK BUY + SLIDER CONTROLS
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Your comments, part 2", "Quick Buy redesign & slider controls");

const rows4 = [
  [hcell("You asked"), hcell("Status"), hcell("What it looks like now")],
  [tc("Scrap the Add-to-Cart bar; rebuild the round cart+ icon (top-right of the image, #E4E5E6 at 50%), with a variant selector for products with options"),
   pill("REBUILT", GREEN),
   tc("Done to spec: the round icon sits at the image's top-right, always visible. One-size products add instantly; multi-size products open a small size picker (size + price), tap to add. Click anywhere else to close it.")],
  [tc("Drawer cart slider: remove the 'see more' arrows on mobile"),
   pill("FIXED", GREEN),
   tc("Arrows are gone on phones (swipe scrolls the row); desktop keeps them.")],
  [tc("Drawer cart slider (desktop): too compact — show 4 products"),
   pill("FIXED", GREEN),
   tc("The drawer slider now shows 4 full cards per view.")],
  [tc("Cart page slider title: capitalize to 'Complete Your Order'"),
   pill("FIXED", GREEN),
   tc("Done — 'Complete Your Order'.")],
  [tc("Cart page (mobile): fix the remove-icon position"),
   pill("FIXED", GREEN),
   tc("Same treatment as the drawer (which you confirmed): the bin icon sits top-right of the item, aligned with the title.")],
];
s.addTable(rows4, {
  x: 0.5, y: 1.65, w: 12.33, colW: [4.7, 1.35, 6.28],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.3, 0.72, 0.66, 0.6, 0.85], margin: [3, 5, 3, 5],
});
footer(s, 4);

// =====================================================================
// SLIDE 5 — REC SLIDERS + BANNER + EXCLUSIONS
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Your comments, part 3", "Recommendation sliders, banner & clean-up");

const rows5 = [
  [hcell("You asked"), hcell("Status"), hcell("What it looks like now")],
  [tc("Rec sliders still don't visually match the other product cards (home + product page); price bold; titles bigger; no side margins on mobile"),
   pill("REBUILT", GREEN),
   tc("Root-fixed: recommendation sliders now use the exact same product card as Best Sellers / Recently Viewed — one template, so fonts, star badges, price weight and Quick Buy match by definition. Mobile side margins added.")],
  [tc("Mobile banner margins — also on the live theme"),
   pill("LIVE ✓", TERRA),
   tc("The banner is now full-width on mobile on BOTH the preview and the LIVE site (shipped today; allow up to ~30 min of caching).")],
  [tc("Recs must not show: out-of-stock, freebies/promo SKUs, Backbar SKUs"),
   pill("CONFIRMED", GREEN),
   tc("Confirmed and enforced: sold-out items, ₱0/'FREE…% off' promos and salon (Backbar) SKUs are filtered from every recommendation slider. There's also a manual exclude list (the Excludes tab in the ops sheet) for one-offs — anything added there disappears from recs within ~15 minutes.")],
];
s.addTable(rows5, {
  x: 0.5, y: 1.65, w: 12.33, colW: [4.7, 1.35, 6.28],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.25, 0.9, 1.45], margin: [3, 5, 3, 5],
});
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 6.0, w: 12.33, h: 0.85, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "Heads-up on the home 'Recommended for You' row:  ", options: { bold: true, color: TERRA } },
  { text: "it may look shorter for a few days — that's the filter removing the sold-out items you flagged. It refills with in-stock picks on the engine's next refresh.", options: { color: MUTED } },
], { x: 0.7, y: 6.06, w: 12.0, h: 0.72, fontFace: BF, fontSize: 11, valign: "middle", margin: 0 });
footer(s, 5);

// =====================================================================
// SLIDE 6 — WHAT WE CHECKED
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "What we checked", "Verified before sending this back");

const rows6 = [
  [hcell("Area"), hcell("What we confirmed")],
  [tc("Sticky bar", { bold: true }), tc("Stars + count render under the title; the bar vanishes when the drawer opens and returns on close (tested live, both directions).")],
  [tc("Quick Buy icon", { bold: true }), tc("Icon shows on every card; the size picker opens, lists sizes with prices ('75ml — ₱780'), closes on outside-click and after adding.")],
  [tc("Rec sliders", { bold: true }), tc("Product page, cart and home rows all render the native card — counted the cards and icons on each.")],
  [tc("Cart page", { bold: true }), tc("'Complete Your Order' title; 4-up drawer slider rule; mobile arrow removal — all in place.")],
  [tc("Clean recommendations", { bold: true }), tc("Rails render with the new filter active; the sold-out items from your home-page screenshot no longer appear.")],
  [tc("Live banner", { bold: true }), tc("The fix is on the live theme (file verified); the live homepage picks it up as its cache expires (≤ ~30 min).")],
];
s.addTable(rows6, {
  x: 0.5, y: 1.6, w: 12.33, colW: [2.4, 9.93],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, valign: "middle",
  autoPage: false, rowH: [0.3, 0.78, 0.78, 0.7, 0.7, 0.78, 0.78], margin: [3, 5, 3, 5],
});
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 6.5, w: 12.33, h: 0.5, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "Phone checklist for you:  ", options: { bold: true, color: TERRA } },
  { text: "full-width bar button · cart-page bin icon · slider side margins · banner edges (live site too).", options: { color: MUTED } },
], { x: 0.7, y: 6.55, w: 12.0, h: 0.4, fontFace: BF, fontSize: 10.5, valign: "middle", margin: 0 });
footer(s, 6);

// =====================================================================
// SLIDE 7 — NEXT STEPS
// =====================================================================
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Over to you", "One fresh look, then we go live");

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 12.33, h: 2.05, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 2.35, w: 0.55, h: 0.55, fill: { color: TERRA } });
s.addText("1", { x: 0.72, y: 2.35, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Final review — fresh windows, hard refresh", { x: 1.5, y: 1.85, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText([
  { text: "Home", options: { hyperlink: { url: L("/") }, color: TERRA, bold: true } },
  { text: " (Quick Buy icon, clean recs)      ", options: { color: MUTED } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: TERRA, bold: true } },
  { text: " (icon + size picker)      ", options: { color: MUTED } },
  { text: "Product", options: { hyperlink: { url: L("/products/davines-purifying-shampoo-for-oily-or-dry-dandruff-100ml") }, color: TERRA, bold: true } },
  { text: " (bar: stars, add-in-place, drawer-hide)      ", options: { color: MUTED } },
  { text: "Cart", options: { hyperlink: { url: L("/cart") }, color: TERRA, bold: true } },
  { text: " (title, 4-up slider)", options: { color: MUTED } },
], { x: 1.5, y: 2.3, w: 11.1, h: 0.6, fontFace: BF, fontSize: 11, valign: "top", margin: 0 });
s.addText("Phone: bar button width · bin icon · slider margins · banner edges (preview AND the live site).", { x: 1.5, y: 3.05, w: 11.1, h: 0.32, fontFace: BF, fontSize: 11, italic: true, color: MUTED, margin: 0 });
s.addText("If anything looks unchanged, it's almost certainly a cached tab — new window first, please.", { x: 1.5, y: 3.38, w: 11.1, h: 0.3, fontFace: BF, fontSize: 10.5, color: GRAY, margin: 0 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.05, w: 12.33, h: 1.3, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 4.42, w: 0.55, h: 0.55, fill: { color: GREEN } });
s.addText("2", { x: 0.72, y: 4.42, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Sign off → switch-over", { x: 1.5, y: 4.2, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText("We publish the new theme, turn off the old sticky-cart app (the doubled-up icons disappear, Recently Viewed picks up its Quick Buy), and cancel the $24.99/month subscription (≈ ₱17k/year back).", { x: 1.5, y: 4.56, w: 11.3, h: 0.7, fontFace: BF, fontSize: 11, color: MUTED, margin: 0, valign: "top" });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.7, w: 12.33, h: 0.9, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "While you review:  ", options: { bold: true, color: TERRA } },
  { text: "the old app is still installed on the preview, so its icons appear alongside the new ones until switch-over. Expected — not a bug.", options: { color: MUTED } },
], { x: 0.7, y: 5.78, w: 12.0, h: 0.74, fontFace: BF, fontSize: 11, valign: "middle", margin: 0 });
footer(s, 7);

// =====================================================================
// SLIDE 8 — CLOSING
// =====================================================================
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("BOTTOM LINE", { x: 0.9, y: 1.7, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Round 3 done. The banner's already live.", { x: 0.9, y: 2.2, w: 11.7, h: 1.5, fontFace: HF, fontSize: 36, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "All 14 June-11 items are in: the bar adds in place and hides for the drawer, Quick Buy is the round icon with a size picker, every slider wears the site's own product card, recommendations exclude sold-out/freebie/salon items, and the mobile banner is full-width — on the live store too. ", options: { color: ICE } },
  { text: "One fresh-eyed pass from you and we flip the switch.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 3.7, w: 11.2, h: 1.5, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
s.addText([
  { text: "Open the preview store:  ", options: { color: GRAY } },
  { text: "click here", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "      ·      Questions? Reply on the project thread.", options: { color: GRAY } },
], { x: 0.9, y: 6.5, w: 11.5, h: 0.3, fontFace: BF, fontSize: 12, margin: 0 });

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Preview-Review.pptx" }).then(f => console.log("WROTE", f));
