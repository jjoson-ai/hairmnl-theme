// cwv-deferred-css-parity — enumerate every element whose geometry depends on a
// DEFERRED stylesheet (bd 2u6r / q9aa / pewh, 2026-08-13).
//
// The theme defers 19 stylesheets via `media="print" onload="this.media='all'"`.
// Any layout-affecting rule in one of them produces a reflow when it finally
// lands: the page paints in a pre-CSS state and jumps. On a fast link the sheet
// usually arrives before first paint, so the bug is invisible in the lab and
// only shows up in the field — which is exactly how the mobile .blog__article
// padding jump (CrUX phone CLS p75 0.13) hid for so long.
//
// Method: load the page twice — once with the deferred sheets BLOCKED (the
// pre-arrival paint state a slow phone actually gets) and once normally (the
// settled state) — then diff element geometry. Every element that moves or
// resizes between the two is a latent CLS source, and the fix is to copy the
// responsible rules into critical CSS at a specificity that wins.
//
// Usage: node cwv-deferred-css-parity.mjs <url> <basePort> [mobile|desktop] [blockPattern]
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';

const SHELL = '/Users/y9378348c/.cache/puppeteer/chrome-headless-shell/mac_arm-147.0.7727.57/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const URL_ = process.argv[2];
const BASE = Number(process.argv[3] || 9900);
const PROF = process.argv[4] || 'mobile';
// Default blocks the sheets that carry layout rules. aos/plyr/pswp are
// behaviour/paint-only and blocking them adds noise, but they are included so
// the report is complete — filter with a narrower pattern when triaging one file.
const BLOCK = (process.argv[5] || '*theme-product.css*,*custom-theme-product.css*,*deferred-templates.css*,*deferred-extras.css*,*theme-collection.css*,*custom-theme-collection.css*,*theme-home.css*,*custom-theme-home.css*,*vertex-recommendations.css*')
  .split(',').map(s => s.trim()).filter(Boolean);
// CAND=<file>: inject candidate critical CSS into the BLOCKED arm. If the
// candidate is complete, the blocked arm's geometry converges on the settled
// geometry and the diff list empties — that is the proof the fix removes the
// reflow, and it is deterministic where waiting for a slow network is not.
const CAND = process.env.CAND ? readFileSync(process.env.CAND, 'utf8') : '';
const P = PROF === 'mobile'
  ? { w: 390, h: 844, dpr: 3, mob: true, down: 1.6 * 1024 * 1024 / 8, lat: 150, cpu: 4 }
  : { w: 1440, h: 900, dpr: 1, mob: false, down: 10 * 1024 * 1024 / 8, lat: 40, cpu: 1 };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const withTimeout = (pr, ms, tag) => Promise.race([pr, new Promise((_, j) => setTimeout(() => j(new Error('timeout:' + tag)), ms))]);

const SNAPSHOT = `(function(){
  var out=[], els=document.querySelectorAll('body *'), n=0;
  for (var i=0;i<els.length && n<600;i++){
    var e=els[i];
    if (e.tagName==='SCRIPT'||e.tagName==='STYLE'||e.tagName==='LINK'||e.tagName==='NOSCRIPT') continue;
    var r=e.getBoundingClientRect();
    if (r.width===0 && r.height===0) continue;
    var cls = (typeof e.className==='string' && e.className.trim()) ? '.'+e.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
    out.push({k:n+':'+e.tagName.toLowerCase()+cls, x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height)});
    n++;
  }
  return JSON.stringify({els:out, docH:document.documentElement.scrollHeight});
})()`;

async function load(port, blocked) {
  const proc = spawn(SHELL, ['--headless=new', `--remote-debugging-port=${port}`, '--no-first-run',
    `--user-data-dir=/tmp/dcp${port}`, '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  let ws = null;
  try {
    let u = null;
    for (let k = 0; k < 40 && !u; k++) {
      try { const t = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(x => x.type === 'page'); u = t?.webSocketDebuggerUrl || null; } catch {}
      if (!u) await sleep(250);
    }
    if (!u) throw new Error('no cdp');
    ws = new WebSocket(u);
    await withTimeout(new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error('ws')); }), 15000, 'ws');
    let id = 0; const pend = new Map();
    ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
    const send = (m, q = {}) => withTimeout(new Promise(r => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method: m, params: q })); }), 30000, m);
    const ev = async x => (await send('Runtime.evaluate', { expression: x, awaitPromise: true, returnByValue: true }))?.result?.result?.value;
    await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: P.w, height: P.h, deviceScaleFactor: P.dpr, mobile: P.mob });
    await send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: P.down, uploadThroughput: P.down / 4, latency: P.lat });
    if (P.cpu > 1) await send('Emulation.setCPUThrottlingRate', { rate: P.cpu });
    if (blocked) await send('Network.setBlockedURLs', { urls: BLOCK });
    if (blocked && CAND) {
      await send('Page.addScriptToEvaluateOnNewDocument', { source:
        `(function(){function go(){try{var s=document.createElement('style');s.setAttribute('data-cand','1');` +
        `s.textContent=${JSON.stringify(CAND)};(document.head||document.documentElement).appendChild(s);}catch(e){}}` +
        `if(document.documentElement){go();}else{document.addEventListener('readystatechange',go,{once:true});}})();` });
    }
    await send('Page.navigate', { url: URL_ });
    for (let k = 0; k < 120; k++) { if (await ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(400); }
    await sleep(9000); // let late widgets settle in BOTH arms
    return JSON.parse(await ev(SNAPSHOT));
  } finally { try { ws && ws.close(); } catch {} try { proc.kill('SIGKILL'); } catch {} }
}

async function main() {
  console.log(`\ndeferred-CSS parity — ${PROF} — ${URL_}`);
  console.log(`blocked: ${BLOCK.join(' ')}`);
  const settled = await load(BASE, false);
  const pre = await load(BASE + 1, true);
  const map = new Map(settled.els.map(e => [e.k, e]));
  const diffs = [];
  for (const p of pre.els) {
    const s = map.get(p.k);
    if (!s) continue;
    const dx = s.x - p.x, dy = s.y - p.y, dw = s.w - p.w, dh = s.h - p.h;
    // Elements parked off-screen horizontally (carousel slides at x=-959 etc.)
    // cannot produce a layout shift, and they dominate a naive diff. Require the
    // element to be at least partly within the viewport's horizontal band in one
    // of the two states.
    const onScreen = (p.x + p.w > 0 && p.x < P.w) || (s.x + s.w > 0 && s.x < P.w);
    if (onScreen && (Math.abs(dx) > 1 || Math.abs(dy) > 1 || Math.abs(dw) > 1 || Math.abs(dh) > 1)) {
      diffs.push({ k: p.k, dx, dy, dw, dh, pre: [p.x, p.y, p.w, p.h], settled: [s.x, s.y, s.w, s.h],
        score: Math.abs(dx) + Math.abs(dy) + Math.abs(dw) + Math.abs(dh) });
    }
  }
  diffs.sort((a, b) => b.score - a.score);
  console.log(`  elements compared: ${pre.els.length} pre / ${settled.els.length} settled`);
  console.log(`  docHeight: pre ${pre.docH} -> settled ${settled.docH}  (delta ${settled.docH - pre.docH})`);
  if (CAND) console.log(`  candidate CSS injected into the blocked arm: ${process.env.CAND} (${CAND.length} bytes)`);
  console.log(`  ELEMENTS THAT MOVE/RESIZE when the deferred sheets land: ${diffs.length}`);
  diffs.slice(0, 18).forEach(d => {
    console.log(`    ${String(d.k).slice(0, 56).padEnd(56)} d=[${d.dx},${d.dy},${d.dw},${d.dh}]`);
    console.log(`        pre ${JSON.stringify(d.pre)} -> settled ${JSON.stringify(d.settled)}`);
  });
  if (!diffs.length) console.log('    none — this page is already parity-clean for the blocked sheets.');
  console.log('DONE-PARITY');
}
main().then(() => process.exit(0)).catch(e => { console.log('FATAL ' + String(e.message || e).slice(0, 200)); process.exit(1); });
