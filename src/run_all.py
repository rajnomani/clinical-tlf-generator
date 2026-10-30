"""Run the whole pipeline, then run it a second time and confirm every output is identical.

Run from the project folder:  python src/run_all.py
"""
import hashlib
import subprocess
import sys
from pathlib import Path

STEPS = [
    "make_data.py",
    "table_demographics.py",
    "table_ae_summary.py",
    "listing_ae.py",
    "figure_ae.py",
    "verify_tlfs.py",
]


def run_pipeline():
    for step in STEPS:
        result = subprocess.run([sys.executable, f"src/{step}"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FAILED: {step}")
            print(result.stdout)
            print(result.stderr)
            sys.exit(1)
        print(f"ran   {step}")
        if step == "verify_tlfs.py":
            print(result.stdout)


def snapshot():
    """A fingerprint of every data and output file."""
    files = sorted(list(Path("data").glob("*.csv")) + [p for p in Path("outputs").iterdir() if p.is_file()])
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


print("=== Run 1 ===")
run_pipeline()
first = snapshot()

print("=== Run 2 (to confirm identical results) ===")
run_pipeline()
second = snapshot()

if first == second:
    print(f"Re-run check: all {len(first)} files are identical.")
else:
    changed = [name for name in first if first[name] != second.get(name)]
    print("Re-run check FAILED. Files that changed:", changed)
    sys.exit(1)