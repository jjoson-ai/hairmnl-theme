#!/usr/bin/env node
/**
 * parity-report.mjs — Generate P6 vs P8 side-by-side HTML triage report
 *
 * Reads from parity-screenshots/{p6,p8}/ (written by smoke-09).
 * Writes  parity-screenshots/index.html — open locally in a browser.
 *
 * Usage:
 *   node bin/parity-report.mjs
 *   # or via npm:
 *   npm run parity:report
 *
 * Output structure per row:
 *   P6 LIVE  |  P8 DEV  |  Difference (CSS mix-blend-mode: difference)
 *
 * "Difference" blend mode shows pure black where images are identical
 * and coloured noise where they differ — immediate visual flag for drift.
 *
 * No extra npm deps needed (pure Node 18+ + HTML/CSS).
 */

import { readdir, readFile, writeFile, stat } from 'fs/promises';
import { resolve, join, basename, extname } from 'path';
import { dirname, fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PARITY_DIR = resolve(__dirname, '..', 'parity-screenshots');
const P6_DIR = join(PARITY_DIR, 'p6');
const P8_DIR = join(PARITY_DIR, 'p8');
const OUT_HTML = join(PARITY_DIR, 'index.html');

// ── helpers ──────────────────────────────────────────────────────────────────

async function dirFiles(dir) {
  try {
    const names = await readdir(dir);
    return names.filter((n) => extname(n) === '.png').sort();
  } catch {
    return [];
  }
}

async function toDataUrl(filePath) {
  try {
    const buf = await readFile(filePath);
    return `data:image/png;base64,${buf.toString('base64')}`;
  } catch {
    return null;
  }
}

async function fileKB(filePath) {
  try {
    const s = await stat(filePath);
    return Math.round(s.size / 1024);
  } catch {
    return 0;
  }
}

function labelFromFilename(name) {
  // e.g. "home-desktop.png" → "home / desktop"
  const base = name.replace('.png', '');
  const parts = base.split('-');
  // last part is viewport (desktop|mobile), rest is template label
  const viewport = parts[parts.length - 1];
  const tpl = parts.slice(0, -1).join('-');
  return { tpl, viewport, display: `${tpl} / ${viewport}` };
}

// ── main ─────────────────────────────────────────────────────────────────────

const p6Files = await dirFiles(P6_DIR);
const p8Files = await dirFiles(P8_DIR);

const allFiles = [...new Set([...p6Files, ...p8Files])].sort();

if (allFiles.length === 0) {
  console.error('✗ No PNG files found in parity-screenshots/p6/ or parity-screenshots/p8/');
  console.error('  Run `npm run test:parity` first to capture both themes.');
  process.exit(1);
}

console.log(`→ Building triage report for ${allFiles.length} screenshot(s)…`);

const rows = await Promise.all(
  allFiles.map(async (name) => {
    const p6Path = join(P6_DIR, name);
    const p8Path = join(P8_DIR, name);
    const [p6Data, p8Data] = await Promise.all([toDataUrl(p6Path), toDataUrl(p8Path)]);
    const [p6kb, p8kb] = await Promise.all([fileKB(p6Path), fileKB(p8Path)]);
    const { display } = labelFromFilename(name);
    return { name, display, p6Data, p8Data, p6kb, p8kb };
  })
);

const generated = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';

const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>P6 vs P8 Parity — HairMNL</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f0f0f; color: #e0e0e0;
      padding: 24px;
    }
    header {
      margin-bottom: 32px;
      border-bottom: 1px solid #333;
      padding-bottom: 16px;
    }
    header h1 { font-size: 20px; font-weight: 600; color: #fff; }
    header p { font-size: 13px; color: #888; margin-top: 4px; }
    .legend {
      display: flex; gap: 16px; flex-wrap: wrap;
      margin-top: 12px; font-size: 12px;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-chip {
      display: inline-block; width: 10px; height: 10px;
      border-radius: 2px;
    }
    .chip-p6 { background: #3b82f6; }
    .chip-p8 { background: #10b981; }
    .chip-diff { background: linear-gradient(135deg, #f59e0b, #ef4444); }
    nav {
      display: flex; gap: 8px; flex-wrap: wrap;
      margin-bottom: 24px;
    }
    nav a {
      font-size: 12px; padding: 4px 10px;
      border: 1px solid #333; border-radius: 4px;
      color: #aaa; text-decoration: none;
      background: #1a1a1a;
    }
    nav a:hover { color: #fff; border-color: #555; }

    .section {
      margin-bottom: 48px;
      scroll-margin-top: 16px;
    }
    .section-title {
      font-size: 15px; font-weight: 600;
      color: #fff; margin-bottom: 16px;
      padding: 8px 12px;
      background: #1a1a1a; border-radius: 6px;
      border-left: 3px solid #3b82f6;
    }

    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
    }
    .col-label {
      font-size: 11px; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.06em; color: #888;
      text-align: center; margin-bottom: 6px;
    }
    .col-label .badge {
      display: inline-block; padding: 2px 8px;
      border-radius: 4px; font-size: 10px;
      margin-left: 6px; vertical-align: middle;
    }
    .badge-p6 { background: #1d4ed8; color: #bfdbfe; }
    .badge-p8 { background: #065f46; color: #a7f3d0; }
    .badge-diff { background: #92400e; color: #fde68a; }

    .img-wrap {
      border: 1px solid #2a2a2a; border-radius: 4px;
      overflow: hidden; position: relative;
      background: #1a1a1a;
    }
    .img-wrap img {
      width: 100%; display: block;
      cursor: zoom-in;
    }
    .img-wrap .kb {
      position: absolute; bottom: 4px; right: 6px;
      font-size: 10px; color: #aaa;
      background: rgba(0,0,0,.6); padding: 1px 5px; border-radius: 3px;
    }
    .missing {
      display: flex; align-items: center; justify-content: center;
      height: 120px; color: #555; font-size: 12px;
    }

    /* Diff column: stack P6 + P8 with mix-blend-mode:difference */
    .diff-stack {
      position: relative; width: 100%;
      overflow: hidden;
      background: #000;
      border: 1px solid #2a2a2a; border-radius: 4px;
    }
    .diff-stack .diff-p6,
    .diff-stack .diff-p8 {
      display: block; width: 100%;
    }
    .diff-stack .diff-p8 {
      position: absolute; top: 0; left: 0;
      mix-blend-mode: difference;
    }
    .diff-hint {
      font-size: 11px; color: #555; text-align: center;
      margin-top: 4px;
    }

    /* Lightbox */
    #lb { display:none; position:fixed; inset:0; z-index:999;
          background:rgba(0,0,0,.92); cursor:zoom-out;
          align-items:center; justify-content:center; }
    #lb.open { display:flex; }
    #lb img { max-width:95vw; max-height:95vh; border-radius:4px; }

    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

<header>
  <h1>P6 LIVE vs P8 DEV — Visual Parity Triage Report</h1>
  <p>Generated ${generated} · ${rows.length} captures across 2 themes</p>
  <div class="legend">
    <span class="legend-item"><span class="legend-chip chip-p6"></span>P6 LIVE (theme 131664707683)</span>
    <span class="legend-item"><span class="legend-chip chip-p8"></span>P8 DEV  (theme 141168312419)</span>
    <span class="legend-item"><span class="legend-chip chip-diff"></span>Difference blend — black = identical, colour = drift</span>
  </div>
</header>

<nav>
${rows.map((r) => `  <a href="#${r.name.replace('.png', '')}">${r.display}</a>`).join('\n')}
</nav>

${rows
  .map(
    (r) => `
<div class="section" id="${r.name.replace('.png', '')}">
  <div class="section-title">${r.display}</div>
  <div class="grid">
    <div>
      <div class="col-label">P6 LIVE <span class="badge badge-p6">live</span></div>
      <div class="img-wrap">
        ${r.p6Data
          ? `<img src="${r.p6Data}" alt="P6 ${r.display}" loading="lazy" onclick="lb(this)">`
          : '<div class="missing">not captured</div>'}
        ${r.p6Data ? `<span class="kb">${r.p6kb}KB</span>` : ''}
      </div>
    </div>
    <div>
      <div class="col-label">P8 DEV <span class="badge badge-p8">dev</span></div>
      <div class="img-wrap">
        ${r.p8Data
          ? `<img src="${r.p8Data}" alt="P8 ${r.display}" loading="lazy" onclick="lb(this)">`
          : '<div class="missing">not captured</div>'}
        ${r.p8Data ? `<span class="kb">${r.p8kb}KB</span>` : ''}
      </div>
    </div>
    <div>
      <div class="col-label">Difference <span class="badge badge-diff">diff</span></div>
      ${r.p6Data && r.p8Data
        ? `<div class="diff-stack">
          <img class="diff-p6" src="${r.p6Data}" alt="" aria-hidden="true">
          <img class="diff-p8" src="${r.p8Data}" alt="diff ${r.display}">
        </div>
        <p class="diff-hint">Black = identical · coloured = drift</p>`
        : '<div class="missing">need both captures</div>'}
    </div>
  </div>
</div>`
  )
  .join('\n')}

<div id="lb" role="dialog" onclick="this.classList.remove('open')">
  <img id="lb-img" src="" alt="Full-size preview">
</div>

<script>
function lb(img) {
  document.getElementById('lb-img').src = img.src;
  document.getElementById('lb').classList.add('open');
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') document.getElementById('lb').classList.remove('open');
});
</script>
</body>
</html>`;

await writeFile(OUT_HTML, html, 'utf8');

const kb = Math.round(Buffer.byteLength(html, 'utf8') / 1024);
console.log(`  ✓ Wrote ${OUT_HTML} (${kb}KB)`);
console.log('');
console.log('Open in browser:');
console.log(`  open "${OUT_HTML}"`);
console.log('');
console.log('Triage checklist:');
console.log('  □ For each row: is every coloured region in the diff column intentional?');
console.log('  □ Flag unintentional drift → file bd issue against the relevant P8 section');
console.log('  □ When all intentional: cutover is green-lit on visual parity');
