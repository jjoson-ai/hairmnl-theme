#!/usr/bin/env node

/**
 * layout-thrash-audit.js
 *
 * Read-only analysis script that scans custom-theme.js for forced-reflow
 * (layout-thrashing) patterns and reports which library sections have the
 * most layout-triggering reads.
 *
 * Usage:
 *   node scripts/layout-thrash-audit.js            # default path
 *   node scripts/layout-thrash-audit.js <filepath>  # custom path
 *
 * Exit code: 0 always (this is a reporting tool, not a linter gate).
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const DEFAULT_TARGET = path.resolve(
  __dirname,
  "..",
  "assets",
  "custom-theme.js"
);

const targetFile = process.argv[2] || DEFAULT_TARGET;

// Layout-thrashing property / method patterns to scan for.
// Each entry: { pattern (RegExp), label (string) }
const PATTERNS = [
  // offset* family
  { pattern: /\.offsetWidth\b/g,   label: "offsetWidth" },
  { pattern: /\.offsetHeight\b/g,  label: "offsetHeight" },
  { pattern: /\.offsetTop\b/g,     label: "offsetTop" },
  { pattern: /\.offsetLeft\b/g,    label: "offsetLeft" },
  { pattern: /\.offsetRight\b/g,   label: "offsetRight" },
  { pattern: /\.offsetBottom\b/g,   label: "offsetBottom" },
  { pattern: /\.offsetParent\b/g,   label: "offsetParent" },

  // client* family
  { pattern: /\.clientWidth\b/g,   label: "clientWidth" },
  { pattern: /\.clientHeight\b/g,  label: "clientHeight" },
  { pattern: /\.clientTop\b/g,     label: "clientTop" },
  { pattern: /\.clientLeft\b/g,    label: "clientLeft" },

  // scroll* family
  { pattern: /\.scrollWidth\b/g,   label: "scrollWidth" },
  { pattern: /\.scrollHeight\b/g,  label: "scrollHeight" },
  { pattern: /\.scrollTop\b/g,     label: "scrollTop" },
  { pattern: /\.scrollLeft\b/g,    label: "scrollLeft" },

  // getBoundingClientRect / getClientRects
  { pattern: /\.getBoundingClientRect\s*\(/g,  label: "getBoundingClientRect()" },
  { pattern: /\.getClientRects\s*\(/g,        label: "getClientRects()" },

  // getComputedStyle
  { pattern: /getComputedStyle\s*\(/g,  label: "getComputedStyle()" },

  // innerWidth / innerHeight (force layout on window)
  { pattern: /window\.innerWidth\b/g,  label: "window.innerWidth" },
  { pattern: /window\.innerHeight\b/g, label: "window.innerHeight" },

  // document.documentElement.clientWidth / Height
  { pattern: /document\.documentElement\.clientWidth\b/g,  label: "docEl.clientWidth" },
  { pattern: /document\.documentElement\.clientHeight\b/g, label: "docEl.clientHeight" },
];

// ---------------------------------------------------------------------------
// Section detection — identify library boundaries via comment markers
// ---------------------------------------------------------------------------

// The bundled file uses `// node_modules/...` comments as section dividers.
// We also recognise `// scripts/...` for custom sections at the tail.
const SECTION_MARKER_RE = /^\s*\/\/ (node_modules\/.+|scripts\/.+)\s*$/;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escRegexp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  if (!fs.existsSync(targetFile)) {
    console.error(`File not found: ${targetFile}`);
    process.exit(1);
  }

  const source = fs.readFileSync(targetFile, "utf8");
  const lines = source.split("\n");
  const totalLines = lines.length;

  console.log("===========================================================");
  console.log("  Layout-Thrashing Audit — custom-theme.js");
  console.log("===========================================================");
  console.log(`  File : ${targetFile}`);
  console.log(`  Lines: ${totalLines}`);
  console.log("");

  // -----------------------------------------------------------------------
  // 1. Build section map
  // -----------------------------------------------------------------------
  const sections = []; // { name, startLine, endLine }

  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(SECTION_MARKER_RE);
    if (m) {
      sections.push({
        name: m[1].trim(),
        startLine: i + 1, // 1-indexed
        endLine: totalLines,
      });
    }
  }

  // Fix endLine: each section ends where the next one begins — 1
  for (let i = 0; i < sections.length - 1; i++) {
    sections[i].endLine = sections[i + 1].startLine - 1;
  }

  // Group fine-grained swiper modules under a single "Swiper" umbrella
  // for readability, but keep the sub-section names for detail.
  const LIBRARY_GROUPS = [
    { prefix: "node_modules/sticky-js/", groupLabel: "Sticky.js" },
    { prefix: "node_modules/he/", groupLabel: "he (HTML entities)" },
    { prefix: "node_modules/sweetalert2/", groupLabel: "SweetAlert2" },
    { prefix: "node_modules/swiper/", groupLabel: "Swiper" },
    { prefix: "node_modules/ssr-window/", groupLabel: "Swiper (ssr-window)" },
    { prefix: "node_modules/dom7/", groupLabel: "Swiper (dom7)" },
    { prefix: "scripts/", groupLabel: "Custom scripts" },
  ];

  function getGroupLabel(sectionName) {
    for (const g of LIBRARY_GROUPS) {
      if (sectionName.startsWith(g.prefix)) return g.groupLabel;
    }
    // Anything else under node_modules gets its own label
    if (sectionName.startsWith("node_modules/")) {
      return sectionName.replace("node_modules/", "");
    }
    return sectionName;
  }

  // -----------------------------------------------------------------------
  // 2. Scan for layout-read patterns
  // -----------------------------------------------------------------------

  // Global counts
  const globalCounts = {};
  for (const p of PATTERNS) {
    globalCounts[p.label] = 0;
  }

  // Per-line hits (for detailed output)
  const lineHits = []; // { line, col, label, text }

  // Per-section counts  { sectionName: { label: count } }
  const sectionCounts = {};
  for (const s of sections) {
    sectionCounts[s.name] = {};
    for (const p of PATTERNS) {
      sectionCounts[s.name][p.label] = 0;
    }
  }

  // Determine which section a 1-indexed line belongs to
  function findSection(lineNum) {
    for (let i = sections.length - 1; i >= 0; i--) {
      if (lineNum >= sections[i].startLine) return sections[i];
    }
    return null;
  }

  // Scan each line
  for (let i = 0; i < lines.length; i++) {
    const lineText = lines[i];
    const lineNum = i + 1;

    for (const p of PATTERNS) {
      // Reset regex lastIndex for each line
      p.pattern.lastIndex = 0;
      let match;
      while ((match = p.pattern.exec(lineText)) !== null) {
        globalCounts[p.label]++;

        const section = findSection(lineNum);
        const sectionName = section ? section.name : "(preamble)";

        if (!sectionCounts[sectionName]) {
          sectionCounts[sectionName] = {};
          for (const pp of PATTERNS) sectionCounts[sectionName][pp.label] = 0;
        }
        sectionCounts[sectionName][p.label]++;

        lineHits.push({
          line: lineNum,
          col: match.index + 1,
          label: p.label,
          text: lineText.trim(),
          section: sectionName,
        });
      }
    }
  }

  // -----------------------------------------------------------------------
  // 3. Print global summary
  // -----------------------------------------------------------------------
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Global Pattern Counts");
  console.log("─────────────────────────────────────────────────────────");

  const sortedGlobals = Object.entries(globalCounts)
    .filter(([, c]) => c > 0)
    .sort((a, b) => b[1] - a[1]);

  if (sortedGlobals.length === 0) {
    console.log("  (no forced-reflow patterns found)");
  } else {
    const maxLabelLen = Math.max(...sortedGlobals.map(([l]) => l.length));
    for (const [label, count] of sortedGlobals) {
      const pad = " ".repeat(Math.max(0, maxLabelLen - label.length));
      const bar = "█".repeat(Math.min(count, 50));
      console.log(`  ${label}${pad}  ${String(count).padStart(4)}  ${bar}`);
    }
  }

  const totalHits = sortedGlobals.reduce((sum, [, c]) => sum + c, 0);
  console.log("");
  console.log(`  Total forced-reflow reads: ${totalHits}`);
  console.log("");

  // -----------------------------------------------------------------------
  // 4. Print per-library-group summary
  // -----------------------------------------------------------------------
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Layout Reads by Library Section");
  console.log("─────────────────────────────────────────────────────────");

  // Aggregate by group label
  const groupAgg = {};
  for (const [sectionName, counts] of Object.entries(sectionCounts)) {
    const group = getGroupLabel(sectionName);
    if (!groupAgg[group]) groupAgg[group] = 0;
    for (const c of Object.values(counts)) groupAgg[group] += c;
  }

  const sortedGroups = Object.entries(groupAgg)
    .filter(([, c]) => c > 0)
    .sort((a, b) => b[1] - a[1]);

  if (sortedGroups.length === 0) {
    console.log("  (no hits in any section)");
  } else {
    const maxGroupLen = Math.max(...sortedGroups.map(([g]) => g.length));
    for (const [group, count] of sortedGroups) {
      const pad = " ".repeat(Math.max(0, maxGroupLen - group.length));
      const bar = "█".repeat(Math.min(count, 50));
      console.log(`  ${group}${pad}  ${String(count).padStart(4)}  ${bar}`);
    }
  }
  console.log("");

  // -----------------------------------------------------------------------
  // 5. Hotspot detail — show sections with the most reads, broken by pattern
  // -----------------------------------------------------------------------
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Hotspot Detail (top sections by read count)");
  console.log("─────────────────────────────────────────────────────────");

  // Aggregate per section by group, preserving sub-section detail
  const sectionDetail = {}; // groupLabel -> [{ subSection, patternCounts }]
  for (const [sectionName, counts] of Object.entries(sectionCounts)) {
    const group = getGroupLabel(sectionName);
    if (!sectionDetail[group]) sectionDetail[group] = [];
    const total = Object.values(counts).reduce((s, c) => s + c, 0);
    sectionDetail[group].push({ subSection: sectionName, counts, total });
  }

  // Sort groups by their total hit count descending
  const groupsByHits = Object.entries(sectionDetail)
    .map(([group, subs]) => {
      const groupTotal = subs.reduce((s, sub) => s + sub.total, 0);
      return { group, subs, groupTotal };
    })
    .sort((a, b) => b.groupTotal - a.groupTotal);

  for (const { group, subs, groupTotal } of groupsByHits) {
    if (groupTotal === 0) continue;

    console.log("");
    console.log(`  ▸ ${group}  (${groupTotal} reads)`);

    // Sort sub-sections by total descending
    subs.sort((a, b) => b.total - a.total);

    for (const { subSection, counts, total } of subs) {
      if (total === 0) continue;
      // Short label: strip node_modules/ prefix
      const shortLabel = subSection.replace(/^node_modules\//, "");
      const activePatterns = Object.entries(counts)
        .filter(([, c]) => c > 0)
        .sort((a, b) => b[1] - a[1])
        .map(([label, c]) => `${label}×${c}`)
        .join(", ");
      console.log(`    ${shortLabel}`);
      console.log(`      ${activePatterns}`);
    }
  }

  // -----------------------------------------------------------------------
  // 6. Print worst individual lines (top 20 by hit density)
  // -----------------------------------------------------------------------
  console.log("");
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Top 20 Offending Lines (most reads on a single line)");
  console.log("─────────────────────────────────────────────────────────");

  // Aggregate line hits
  const lineAgg = {};
  for (const h of lineHits) {
    const key = h.line;
    if (!lineAgg[key]) lineAgg[key] = { count: 0, labels: [], text: h.text, section: h.section };
    lineAgg[key].count++;
    lineAgg[key].labels.push(h.label);
  }

  const worstLines = Object.entries(lineAgg)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 20);

  if (worstLines.length === 0) {
    console.log("  (no offending lines found)");
  } else {
    for (const [lineNum, info] of worstLines) {
      const uniqueLabels = [...new Set(info.labels)].sort();
      const labelStr = uniqueLabels.join(", ");
      const truncated = info.text.length > 100
        ? info.text.slice(0, 97) + "..."
        : info.text;
      const group = getGroupLabel(info.section);
      console.log(
        `  L${lineNum.padStart(5)} │ ${String(info.count).padStart(2)} reads │ ${group.padEnd(20)} │ ${labelStr}`
      );
      console.log(`          │ ${truncated}`);
    }
  }

  // -----------------------------------------------------------------------
  // 7. Print read-write interleaving warning patterns
  // -----------------------------------------------------------------------
  console.log("");
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Read-Write Interleave Risk (potential thrash loops)");
  console.log("─────────────────────────────────────────────────────────");
  console.log("");
  console.log("  Checking for patterns where layout reads follow style");
  console.log("  writes within a few lines — the classic forced-reflow");
  console.log("  pattern that causes layout thrashing.");
  console.log("");

  // Simple heuristic: find lines that write to .style.* or setProperty,
  // then check if nearby lines (within 3 lines) read layout properties.
  const WRITE_RE = /\.style\[|\.style\.|setProperty\(/;
  const layoutReadLabels = new Set(PATTERNS.map((p) => p.label));

  // Build a set of line numbers that have reads
  const readLineNums = new Set(lineHits.map((h) => h.line));

  let interleaveWarnings = 0;

  for (let i = 0; i < lines.length; i++) {
    if (!WRITE_RE.test(lines[i])) continue;
    const writeLine = i + 1;

    // Check ±3 lines for reads
    for (let offset = -3; offset <= 3; offset++) {
      if (offset === 0) continue;
      const checkLine = writeLine + offset;
      if (checkLine < 1 || checkLine > lines.length) continue;
      if (!readLineNums.has(checkLine)) continue;

      const hits = lineHits.filter((h) => h.line === checkLine);
      const labels = [...new Set(hits.map((h) => h.label))];
      const section = findSection(checkLine);
      const group = section ? getGroupLabel(section.name) : "(unknown)";

      const writeText = lines[i].trim().length > 80
        ? lines[i].trim().slice(0, 77) + "..."
        : lines[i].trim();
      const readText = lines[checkLine - 1].trim().length > 80
        ? lines[checkLine - 1].trim().slice(0, 77) + "..."
        : lines[checkLine - 1].trim();

      console.log(`  ⚠  Write at L${writeLine}, Read at L${checkLine} (${labels.join(", ")})`);
      console.log(`     Section : ${group}`);
      console.log(`     Write    : ${writeText}`);
      console.log(`     Read     : ${readText}`);
      console.log("");
      interleaveWarnings++;
    }
  }

  if (interleaveWarnings === 0) {
    console.log("  ✓ No obvious write-then-read interleave patterns found.");
  } else {
    console.log(`  Found ${interleaveWarnings} potential write→read interleave(s).`);
  }

  // -----------------------------------------------------------------------
  // 8. Summary
  // -----------------------------------------------------------------------
  console.log("");
  console.log("─────────────────────────────────────────────────────────");
  console.log("  Summary");
  console.log("─────────────────────────────────────────────────────────");
  console.log(`  Total layout-read hits      : ${totalHits}`);
  console.log(`  Distinct patterns found     : ${sortedGlobals.length}`);
  console.log(`  Library sections with hits  : ${sortedGroups.length}`);
  console.log(`  Write→read interleave risks : ${interleaveWarnings}`);
  console.log("");
  console.log("  Priority: Focus on sections with the highest read counts,");
  console.log("  especially those in event handlers (scroll, resize, mouse)");
  console.log("  where layout thrashing causes the worst INP / jank impact.");
  console.log("===========================================================");
}

main();