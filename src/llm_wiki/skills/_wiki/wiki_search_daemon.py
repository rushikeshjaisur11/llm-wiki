#!/usr/bin/env python3
"""
wiki_search_daemon.py — long-lived search daemon.

Keeps SentenceTransformer model + SQLite connections warm in memory.
Client (search.py) connects via TCP localhost; port written to wiki/.daemon_port.
Auto-shuts down after 30 min of idle.

Usage:
  # Start in background (Windows):
  pythonw C:/Users/rushi/.claude/skills/_wiki/wiki_search_daemon.py

  # Start in foreground (debug):
  python wiki_search_daemon.py

  # Stop:
  python wiki_search_daemon.py --stop

Protocol (newline-delimited JSON):
  Request:  {"query": "...", "top": 5, "debug": false}
  Response: {"results": ["path1.md", ...], "error": null}
  Stop:     {"command": "stop"}
"""

import json
import os
import signal
import socket
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_graph import VAULT
from search import _local_search, _get_model

HOST         = "127.0.0.1"
PORT_FILE    = VAULT / "wiki" / ".daemon_port"
IDLE_TIMEOUT = 30 * 60   # seconds

_last_activity: float = time.monotonic()
_server: socket.socket | None = None


# ── Request handler ───────────────────────────────────────────────────────────

def _handle(conn: socket.socket) -> None:
    global _last_activity
    try:
        buf = b""
        while b"\n" not in buf:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk

        line = buf.split(b"\n")[0]
        if not line:
            return

        req = json.loads(line.decode("utf-8"))

        if req.get("command") == "stop":
            conn.sendall(b'{"ok":true}\n')
            conn.close()
            _shutdown()
            return

        query   = req.get("query", "")
        top     = int(req.get("top", 5))
        debug   = bool(req.get("debug", False))
        results = _local_search(query, top=top, debug=debug)
        conn.sendall((json.dumps({"results": results, "error": None}) + "\n").encode())
        _last_activity = time.monotonic()

    except Exception as exc:
        try:
            conn.sendall((json.dumps({"results": [], "error": str(exc)}) + "\n").encode())
        except Exception:
            pass
    finally:
        conn.close()


# ── Idle watchdog ─────────────────────────────────────────────────────────────

def _watchdog() -> None:
    while True:
        time.sleep(60)
        if time.monotonic() - _last_activity > IDLE_TIMEOUT:
            print(f"[daemon] {IDLE_TIMEOUT // 60} min idle — shutting down", flush=True)
            _shutdown()


def _shutdown() -> None:
    PORT_FILE.unlink(missing_ok=True)
    if _server:
        try:
            _server.close()
        except Exception:
            pass
    os._exit(0)


# ── Client-side stop ──────────────────────────────────────────────────────────

def _send_stop() -> None:
    if not PORT_FILE.exists():
        print("No daemon running (port file missing).")
        return
    port = int(PORT_FILE.read_text().strip())
    try:
        s = socket.create_connection((HOST, port), timeout=3)
        s.sendall(b'{"command":"stop"}\n')
        s.recv(64)
        s.close()
        print("Daemon stopped.")
    except Exception:
        PORT_FILE.unlink(missing_ok=True)
        print("Daemon not responding — stale port file removed.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    global _server

    if "--stop" in sys.argv:
        _send_stop()
        return

    # Warm up model before accepting connections
    print("[daemon] loading model...", flush=True)
    _get_model()
    print("[daemon] model ready", flush=True)

    _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _server.bind((HOST, 0))
    port = _server.getsockname()[1]
    _server.listen(8)

    PORT_FILE.write_text(str(port))
    print(f"[daemon] listening on {HOST}:{port}  pid={os.getpid()}", flush=True)

    threading.Thread(target=_watchdog, daemon=True).start()

    signal.signal(signal.SIGINT,  lambda *_: _shutdown())
    signal.signal(signal.SIGTERM, lambda *_: _shutdown())

    while True:
        try:
            conn, _ = _server.accept()
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()
        except OSError:
            break


if __name__ == "__main__":
    main()
