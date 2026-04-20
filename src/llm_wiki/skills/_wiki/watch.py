#!/usr/bin/env python3
"""
watch.py — live vault file watcher. Auto-rebuilds search indexes on .md changes.

Watches vault for Create / Modify / Move events on *.md files.
Debounces 2 s to coalesce rapid autosave bursts.
On trigger: runs all builders with --update <path> (incremental, fast).

Dependencies: pip install watchdog

Usage:
  python watch.py              # start watching (blocks; Ctrl-C to stop)
  python watch.py --verbose    # log every filesystem event
"""

import sys
import subprocess
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_graph import VAULT

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    print("watchdog not installed.\n  pip install watchdog")
    sys.exit(1)

SCRIPTS   = Path(__file__).parent
DEBOUNCE  = 2.0   # seconds

INCLUDE_TOPS = {
    "research", "learning", "data-engineering",
    "projects", "personal", "archive",
}

# Paths to track: pending[rel_path] = timestamp of last event
_pending: dict[str, float] = {}
_lock    = threading.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _vault_rel(abs_path: str) -> str | None:
    """Return vault-relative posix path if the file is an includable .md note."""
    try:
        rel = Path(abs_path).relative_to(VAULT).as_posix()
    except ValueError:
        return None
    if not rel.endswith(".md"):
        return None
    if rel.split("/")[0] not in INCLUDE_TOPS:
        return None
    return rel


def _rebuild(rel: str, verbose: bool) -> None:
    print(f"[watch] rebuilding: {rel}", flush=True)

    builders = [
        [sys.executable, str(SCRIPTS / "build_graph.py"),   "--update", rel],
        [sys.executable, str(SCRIPTS / "build_routing.py"), "--update", rel],
        [sys.executable, str(SCRIPTS / "build_index.py"),   "--update", rel],
    ]
    emb = SCRIPTS / "build_embeddings.py"
    if emb.exists():
        builders.append([sys.executable, str(emb), "--update", rel])

    for cmd in builders:
        result = subprocess.run(cmd, capture_output=not verbose, text=True)
        if result.returncode != 0:
            name = Path(cmd[1]).name
            print(f"  [error] {name}: {result.stderr.strip()}", flush=True)

    print(f"[watch] done:        {rel}", flush=True)


# ── Debounce loop (runs in background thread) ─────────────────────────────────

def _debounce_loop(verbose: bool) -> None:
    while True:
        time.sleep(0.5)
        now = time.monotonic()
        with _lock:
            due = [p for p, t in _pending.items() if now - t >= DEBOUNCE]
            for p in due:
                del _pending[p]
        for p in due:
            _rebuild(p, verbose)


# ── Watchdog event handler ────────────────────────────────────────────────────

class _Handler(FileSystemEventHandler):
    def __init__(self, verbose: bool) -> None:
        self._verbose = verbose

    def _enqueue(self, path: str) -> None:
        rel = _vault_rel(path)
        if rel:
            if self._verbose:
                print(f"[watch] event:   {rel}", flush=True)
            with _lock:
                _pending[rel] = time.monotonic()

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(str(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(str(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(str(event.dest_path))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    verbose = "--verbose" in sys.argv

    print(f"[watch] vault:    {VAULT}", flush=True)
    print(f"[watch] debounce: {DEBOUNCE}s | Ctrl-C to stop", flush=True)

    threading.Thread(target=_debounce_loop, args=(verbose,), daemon=True).start()

    observer = Observer()
    observer.schedule(_Handler(verbose), str(VAULT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watch] stopping...", flush=True)
        observer.stop()
    observer.join()
    print("[watch] stopped.", flush=True)


if __name__ == "__main__":
    main()
