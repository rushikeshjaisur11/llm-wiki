# GRADER TEMPLATE — used by /curriculum F3
#
# How to use:
#   1. Read the day's practical.md `## Required outputs` table.
#   2. Read this template.
#   3. Replace the per-output example blocks below with one block per row in the Required outputs table.
#      Match file paths EXACTLY to the table — never invent different names.
#   4. Write the adapted script to curricula/<slug>/day-<nn>/grader.py via Bash (never Write tool).
#   5. Run it via: python curricula/<slug>/day-<nn>/grader.py
#
# Supported output types:
#   .csv  → pandas shape + column presence + null checks
#   .json → key presence + type checks
#   .pkl  → pickle.load() succeeds (no exception)
#   .pt   → torch.load() succeeds
#   .png  → existence check only

# Auto-generated grader for day <N> — <topic>
# Checks that Required outputs exist and meet structural requirements.
# Run: python curricula/<slug>/day-<nn>/grader.py

import pathlib, sys, json
import pandas as pd   # remove if no CSV outputs

ROOT = pathlib.Path("{{VAULT}}")
OUTPUTS = ROOT / "curricula/<slug>/day-<nn>/outputs"
results = []

def check(label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    results.append(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    return cond

# ── per output file — adapt one block per row in Required outputs table ───────

# Example for a CSV output:
p = OUTPUTS / "day-<nn>-<artifact>.csv"
check("day-<nn>-<artifact>.csv exists", p.exists())
if p.exists():
    df = pd.read_csv(p)
    check("row count reasonable", len(df) > 0, f"got {len(df)} rows")
    check("expected columns present", {"col1", "col2"}.issubset(df.columns),
          f"found {list(df.columns)}")
    check("no nulls in col1", df["col1"].notna().all())

# Example for a JSON output:
p2 = OUTPUTS / "day-<nn>-<artifact2>.json"
check("day-<nn>-<artifact2>.json exists", p2.exists())
if p2.exists():
    data = json.loads(p2.read_text())
    check("required keys present", {"key1", "key2"}.issubset(data.keys()))
    check("key1 is numeric", isinstance(data.get("key1"), (int, float)))

# Example for a .pkl output:
# import pickle
# p3 = OUTPUTS / "day-<nn>-model.pkl"
# check("day-<nn>-model.pkl exists", p3.exists())
# if p3.exists():
#     try:
#         pickle.load(open(p3, "rb"))
#         check("pickle loads without error", True)
#     except Exception as e:
#         check("pickle loads without error", False, str(e))

# Example for a .pt output:
# import torch
# p4 = OUTPUTS / "day-<nn>-model.pt"
# check("day-<nn>-model.pt exists", p4.exists())
# if p4.exists():
#     try:
#         torch.load(p4, weights_only=True)
#         check("torch checkpoint loads", True)
#     except Exception as e:
#         check("torch checkpoint loads", False, str(e))

# Example for a .png output (existence only):
# p5 = OUTPUTS / "day-<nn>-plot.png"
# check("day-<nn>-plot.png exists", p5.exists())

# ── summary ──────────────────────────────────────────────────────────────────
passed = sum(1 for r in results if r.startswith("[PASS]"))
failed = sum(1 for r in results if r.startswith("[FAIL]"))
print("\n".join(results))
print(f"\n{'PASS' if failed == 0 else 'FAIL'} — {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
