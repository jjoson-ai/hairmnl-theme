#!/usr/bin/env python3
"""Shared GTM helpers — workspace resolution.

WHY THIS EXISTS (bd hairmnl-theme-6spt, 2026-08-16)
---------------------------------------------------
Every gtm-*.py script used to hardcode `WORKSPACE_ID = "190"` (or "192").
Those ids went stale. By 2026-08-16:

  workspace 190  ->  131 tags, 63 DEAD Universal Analytics tags
  workspace 192  ->   66 tags
  workspace 197  ->   38 tags, 0 UA   <- the real Default Workspace
  LIVE VERSION 145 ->  38 tags, 0 UA  <- what is actually published

So an audit reading 190 described a container that had not existed for a long
time. That false picture became a proposal to delete 224 entities from
production (bd z3z1, closed invalid). Nothing was deleted — the staging
workspace correctly reported zero UA tags to remove — but the near-miss is the
reason this module exists.

Worse, 190 and 192 do NOT appear in `workspaces().list()` and `workspaces().get()`
returns 404 for them, yet their entity-list endpoints still return data. A stale
id therefore fails LOUDLY nowhere: it silently serves a plausible, wrong answer.

RULES
-----
1. Never hardcode a workspace id. Call `resolve_workspace_path()`.
2. For any claim about what is actually PUBLISHED, prefer
   `svc.accounts().containers().versions().live(parent=...)`. The live version
   is authoritative; a workspace is only a working copy.
"""
import socket
import sys
import time

# httplib2 (used by googleapiclient) inherits the process-wide default socket
# timeout, which on this machine is short enough that tagmanager.googleapis.com
# connects fail intermittently — observed repeatedly on 2026-08-16, including a
# mid-run failure of gtm-audit.py. Raise it once, on import, for every caller.
if socket.getdefaulttimeout() is None or socket.getdefaulttimeout() < 120:
    socket.setdefaulttimeout(120)

_CACHE: dict[tuple[str, str], str] = {}


def retry(fn, tries: int = 5, label: str = ""):
    """Call `fn`, retrying transient network failures with linear backoff.

    The GTM API on this machine throws bare socket TimeoutError on connect often
    enough that a single attempt is not reliable. Raises the last error if every
    attempt fails.
    """
    last = None
    for attempt in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — transport errors are the point
            last = e
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
    raise last


def resolve_workspace_id(svc, account_id: str, container_id: str,
                         fallback: str | None = None) -> str:
    """Return the container's CURRENT default workspace id.

    Prefers the workspace literally named "Default Workspace"; otherwise the
    lowest-numbered visible workspace. Falls back to `fallback` only if the
    lookup fails outright, and says so on stderr — a stale fallback should be
    noisy, never silent.
    """
    key = (account_id, container_id)
    if key in _CACHE:
        return _CACHE[key]
    parent = f"accounts/{account_id}/containers/{container_id}"
    try:
        wss = retry(
            lambda: svc.accounts().containers().workspaces().list(
                parent=parent).execute(),
            label="workspace list").get("workspace", [])
        chosen = next((w for w in wss if w.get("name") == "Default Workspace"), None)
        if chosen is None and wss:
            chosen = min(wss, key=lambda w: int(w["workspaceId"]))
        if chosen is None:
            raise RuntimeError("container reports no workspaces")
        wid = chosen["workspaceId"]
        if fallback and wid != fallback:
            print(f"  NOTE: resolved default workspace {wid} "
                  f"(hardcoded fallback {fallback} is STALE — see bd 6spt)",
                  file=sys.stderr)
        _CACHE[key] = wid
        return wid
    except Exception as e:
        if fallback:
            print(f"  WARN: workspace resolve failed ({e}); falling back to "
                  f"{fallback}, which may be STALE — verify against "
                  f"versions().live() before trusting any output.", file=sys.stderr)
            return fallback
        raise


def resolve_workspace_path(svc, account_id: str, container_id: str,
                           fallback: str | None = None) -> str:
    """Full `accounts/*/containers/*/workspaces/*` path for the default workspace."""
    wid = resolve_workspace_id(svc, account_id, container_id, fallback)
    return f"accounts/{account_id}/containers/{container_id}/workspaces/{wid}"
