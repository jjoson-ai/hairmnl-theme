// Instrument validation: does this browser binary actually report layout shifts?
// Serves a local page that shifts a known amount, computes the EXPECTED CLS
// analytically, and compares. A binary that reports ~0 here cannot be trusted
// to report 0 on a real page — which is exactly how two agents (and one of my
// own runs) produced false "no shift" results.
//
// Usage: node instrument-check.mjs <app|shell> <port>
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';

const BIN = process.argv[2] === 'shell'
  ? '/Users/y9378348c/.cache/puppeteer/chrome-headless-shell/mac_arm-147.0.7727.57/chrome-headless-shell-mac-arm64/chrome-headless-shell'
  : '/Users/y9378348c/.cache/puppeteer/chrome/mac_arm-147.0.7727.57/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';
const PORT = Number(process.argv[3] || 9990);
const HTTP = PORT + 1000;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const withTimeout = (pr, ms, tag) => Promise.race([pr, new Promise((_, j) => setTimeout(() => j(new Error('timeout:' + tag)), ms))]);

// Viewport 1000x800. A 100px-tall block is inserted at t=1.5s above a 200px-tall
// text div that starts at y=0. Impact fraction = (200+100)/800 = 0.375,
// distance fraction = 100/800 = 0.125  ->  expected CLS = 0.046875
const PAGE = `<!doctype html><html><head><style>
body{margin:0}#t{height:200px;background:#eee;font:16px sans-serif}#ins{height:100px;background:#f99;display:none}
</style></head><body><div id="ins"></div><div id="t">shift target</div>
<script>setTimeout(function(){document.getElementById('ins').style.display='block';},1500);</script>
</body></html>`;

const OBS = `window.__cls=0;window.__n=0;
try{new PerformanceObserver(function(l){for(const e of l.getEntries()){if(e.hadRecentInput)continue;window.__cls+=e.value;window.__n++;}}).observe({type:'layout-shift',buffered:true});}catch(e){window.__e=String(e);}
window.__raf=0;(function tick(){window.__raf++;requestAnimationFrame(tick);})();`;

async function main() {
  const srv = createServer((_, res) => { res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(PAGE); });
  await new Promise(r => srv.listen(HTTP, '127.0.0.1', r));
  const proc = spawn(BIN, ['--headless=new', `--remote-debugging-port=${PORT}`, '--no-first-run',
    `--user-data-dir=/tmp/instr${PORT}`, '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  let ws = null;
  try {
    let u = null;
    for (let k = 0; k < 40 && !u; k++) {
      try { const t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(x => x.type === 'page'); u = t?.webSocketDebuggerUrl || null; } catch {}
      if (!u) await sleep(250);
    }
    if (!u) throw new Error('no cdp endpoint');
    ws = new WebSocket(u);
    await withTimeout(new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error('ws')); }), 15000, 'ws');
    let id = 0; const pend = new Map();
    ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
    const send = (m, q = {}) => withTimeout(new Promise(r => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method: m, params: q })); }), 30000, m);
    const ev = async x => (await send('Runtime.evaluate', { expression: x, awaitPromise: true, returnByValue: true }))?.result?.result?.value;
    await send('Page.enable'); await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 800, deviceScaleFactor: 1, mobile: false });
    await send('Page.addScriptToEvaluateOnNewDocument', { source: OBS });
    await send('Page.navigate', { url: `http://127.0.0.1:${HTTP}/` });
    for (let k = 0; k < 60; k++) { if (await ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(300); }
    await sleep(4000);
    const raf = await ev('window.__raf');
    const cls = await ev('window.__cls');
    const n = await ev('window.__n');
    const paints = await ev(`performance.getEntriesByType('paint').length`);
    const moved = await ev(`document.getElementById('t').getBoundingClientRect().top`);
    const EXPECTED = 0.046875;
    const ok = typeof cls === 'number' && Math.abs(cls - EXPECTED) < 0.01 && n > 0;
    console.log(JSON.stringify({
      binary: process.argv[2] === 'shell' ? 'chrome-headless-shell' : 'Chrome for Testing (app)',
      rafTicks: raf, paintEntries: paints, shiftEntries: n,
      clsReported: cls, clsExpected: EXPECTED,
      targetMovedToY: moved,
      VERDICT: ok ? 'INSTRUMENT OK' : 'INSTRUMENT BROKEN — reports no/low shift despite a real 100px shift',
    }, null, 1));
  } finally {
    try { ws && ws.close(); } catch {}
    try { proc.kill('SIGKILL'); } catch {}
    srv.close();
  }
}
main().then(() => process.exit(0)).catch(e => { console.log(JSON.stringify({ FATAL: String(e.message || e) })); process.exit(1); });
