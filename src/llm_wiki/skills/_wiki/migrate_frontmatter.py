#!/usr/bin/env python3
"""
migrate_frontmatter.py — one-shot frontmatter schema normaliser

Canonical schema:  title | created | updated | tags | type | source | related

Transformations applied to every .md in the vault:
  1. date / date-imported  →  created
  2. Add `updated` = created value if missing
  3. Add `title` from first "# Heading" in body if missing
  4. Add `type: ""` if missing
  5. Add `source: ""` if missing
  6. Add `related: []` if missing
  7. Reorder frontmatter keys to canonical order (unknown keys appended at end)

Dry-run by default.  Pass --write to apply changes.

Usage:
  python migrate_frontmatter.py            # dry-run, shows diff summary
  python migrate_frontmatter.py --write    # apply all changes in-place
"""

import re
import sys
from pathlib import Path

import yaml

# ── Config ───────────────────────────────────────────────────────────────────

VAULT_PATH_FILE = Path(__file__).parent / ".vault_path"
VAULT = Path(VAULT_PATH_FILE.read_text(encoding="utf-8").strip())

INCLUDE_DIRS = {"research", "learning", "data-engineering", "projects", "personal", "daily", "archive"}
SKIP_PREFIXES = {"wiki/", "inbox/"}

CANONICAL_ORDER = ["title", "created", "updated", "tags", "type", "source", "related"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def find_notes():
    for md in sorted(VAULT.rglob("*.md")):
        rel = md.relative_to(VAULT).as_posix()
        top = rel.split("/")[0]
        if top not in INCLUDE_DIRS:
            continue
        if any(rel.startswith(p) for p in SKIP_PREFIXES):
            continue
        yield md


def split_frontmatter(text: str):
    """Return (frontmatter_str_or_None, body_str)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm_str = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    return fm_str, body


def extract_title_from_body(body: str) -> str:
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+)", line)
        if m:
            return m.group(1).strip()
    return ""


def normalise(fm: dict, body: str, path: Path) -> dict:
    out = dict(fm)

    # 1. Rename date aliases → created
    for alias in ("date", "date-imported"):
        if alias in out and "created" not in out:
            out["created"] = out.pop(alias)
        elif alias in out:
            del out[alias]

    created_val = out.get("created", "")

    # 2. Add updated if missing
    if "updated" not in out:
        out["updated"] = created_val

    # 3. Add title if missing
    if "title" not in out or not out["title"]:
        title = extract_title_from_body(body)
        if title:
            out["title"] = title

    # 4. Add type if missing
    if "type" not in out:
        out["type"] = ""

    # 5. Add source if missing (don't rename source-count)
    if "source" not in out:
        out["source"] = ""

    # 6. Add related if missing
    if "related" not in out:
        out["related"] = []

    # 7. Reorder: canonical keys first, then any extras
    reordered = {}
    for key in CANONICAL_ORDER:
        if key in out:
            reordered[key] = out[key]
    for key, val in out.items():
        if key not in reordered:
            reordered[key] = val

    return reordered


def fm_to_str(fm: dict) -> str:
    # Use yaml.dump but preserve string quoting for multiline values
    return yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip()


def process(md: Path, write: bool) -> bool:
    """Return True if the file would be / was changed."""
    text = md.read_text(encoding="utf-8")
    fm_str, body = split_frontmatter(text)

    if fm_str is None:
        # No frontmatter at all — create minimal one
        title = extract_title_from_body(body)
        fm = {"title": title, "created": "", "updated": "", "tags": [], "type": "", "source": "", "related": []}
    else:
        try:
            fm = yaml.safe_load(fm_str) or {}
        except yaml.YAMLError as e:
            print(f"  SKIP (yaml error): {md.relative_to(VAULT)} — {e}")
            return False

    new_fm = normalise(fm, body, md)

    if new_fm == fm:
        return False  # nothing changed

    new_text = f"---\n{fm_to_str(new_fm)}\n---\n\n{body}"

    rel = md.relative_to(VAULT).as_posix()
    changed_keys = []
    for k in CANONICAL_ORDER:
        old_val = fm.get(k)
        new_val = new_fm.get(k)
        if old_val != new_val:
            changed_keys.append(f"{k}: {repr(old_val)} → {repr(new_val)}")
    removed = [k for k in fm if k not in new_fm]
    if removed:
        changed_keys.append(f"removed: {removed}")

    print(f"  {'WRITE' if write else 'WOULD'} {rel}")
    for c in changed_keys:
        print(f"      {c}")

    if write:
        md.write_text(new_text, encoding="utf-8")

    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    write = "--write" in sys.argv
    mode = "WRITE MODE" if write else "DRY-RUN (pass --write to apply)"
    print(f"\nmigrate_frontmatter.py — {mode}")
    print(f"Vault: {VAULT}\n")

    changed = 0
    total = 0
    for md in find_notes():
        total += 1
        if process(md, write):
            changed += 1

    print(f"\n{'Applied' if write else 'Would change'} {changed} / {total} files.")
    if not write and changed:
        print("Re-run with --write to apply.\n")


if __name__ == "__main__":
    main()
