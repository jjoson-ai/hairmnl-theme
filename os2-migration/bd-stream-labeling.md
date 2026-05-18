# bd stream labels — categorization rules

Companion to `MIGRATION-CONTRACT.md`. Records how the existing in-flight
`bd` issues were categorized into `stream:a` / `stream:b` / `stream:both`
on 2026-05-18 (yxte aftermath), and the rules for labeling new issues.

## How to read a label

| Label | Meaning |
|---|---|
| `stream:a` | Fix ships to **live theme `131664707683`** ("Pipeline 6 - Fix share image") under the current Pipeline 6.1.3 architecture. Customer-impacting on push. |
| `stream:b` | Fix ships to **dev theme `141168312419`** ("Pipeline 8 Working Demo"). Lands in production at the migration cutover (TBD). No customer impact until cutover. |
| `stream:both` | Touches code or behavior shared by both stream targets. **Requires coordinated review before close.** |

## Categorization rubric

When filing a new issue, apply labels using this decision tree:

1. **Is the fix a continuation of the `ujg6`, `2i8b`, or `80z0` epic?**
   → `stream:b`. These epics live entirely on dev theme `141168312419`.
2. **Does the fix push to live theme `131664707683`?**
   → `stream:a`. (Today's CWV / perf / bug-fix work.)
3. **Does the fix touch `MIGRATION-CONTRACT.md`, `scripts/check-snippet-wiring.py`,
   `os2-migration/intentionally-orphan.txt`, or anything that audits cross-stream
   wiring?**
   → `stream:both`.
4. **Does the fix re-port a stream:a artifact onto stream:b** (or vice versa)?
   → `stream:both`.

Apply with `bd update <id> --add-label stream:<x>`. Multiple labels
allowed; use `stream:both` PLUS the dominant stream label if helpful.

## 2026-05-18 backfill snapshot

42 open/in-progress issues categorized at the time of contract creation:

### stream:b — 19 issues (P8 migration, dev theme target)

All `hairmnl-theme-ujg6.*` children + epic roots:
- `ujg6`, `ujg6.7`, `ujg6.8`, `ujg6.12`, `ujg6.13`, `ujg6.14`, `ujg6.15`,
  `ujg6.16`, `ujg6.17`, `ujg6.18`, `ujg6.19`, `ujg6.20`, `ujg6.26`,
  `ujg6.27`, `ujg6.28`, `ujg6.29`
- `2i8b` (Phase 4 migration epic)
- `80z0` (Mega-epic, OS 2.0 readiness)
- `fsaa` (re-port Reamaze defer onto P8 theme.liquid)

### stream:a — 22 issues (live theme optimization)

- `01vl` epic (Pro Blogger LCP)
- `a7av`, `a7av.1` (Stky replacement)
- `g1n`, `g1n.3` (Back-in-Stock replacement)
- `meu` (Reamaze defer epic)
- `987` (Desktop CLS investigation)
- `yzk` (Tree-shake vendor.js)
- `3q4` (URL redirect)
- `15f` (Elevar tracking)
- `hksd` (PSI follow-up audit)
- Plus various P2/P3 individual bugs (`fcn`, `oyw`, `nra`, `dnb`, `89n`,
  `uj2`, `ary`, `f3i`, `ur0`, `r8r`, `j0g`)

### stream:both — 1 issue (interface)

- `76m9` (audit P4 port for dormant snippets) — by definition touches the
  P6 ↔ P8 wiring interface.

## Labels NOT used

For clarity, this repo only uses the three stream labels above. Other bd
label patterns (priority levels, kind tags, etc.) come from bd's built-in
fields (`--priority`, `--type`) — don't reinvent them as labels.

## Future: when to retire the labels

After the P8 cutover lands and `bd 2i8b` closes, only `stream:a` will
remain meaningful (live = P8 by then). At that point:

1. Remove `stream:b` and `stream:both` from all closed issues (already
   immutable, but reduces noise in queries).
2. Update `MIGRATION-CONTRACT.md` to reflect single-stream operation.
3. Keep the `check-snippet-wiring.py` lint — orphan-snippet detection
   is generically useful even after the migration.
