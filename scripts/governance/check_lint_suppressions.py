#!/usr/bin/env python3
"""Escape-hatch gate: lint suppression ratchet.

Counts ``# noqa`` in Python and ``eslint-disable`` in TypeScript.
Baseline in .memory-layer/baselines/lint-suppressions.json — ratchet only goes DOWN.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".memory-layer/baselines/lint-suppressions.json"

PY_PATTERN = re.compile(r"#\s*noqa")
TS_PATTERN = re.compile(r"eslint-disable")


def count_suppressions(path: pathlib.Path) -> int:
    text = path.read_text(errors="replace")
    pat = PY_PATTERN if path.suffix == ".py" else TS_PATTERN
    return len(pat.findall(text))


def scan() -> int:
    total = 0
    for pattern in ("backend/**/*.py", "frontend/src/**/*.ts"):
        for p in ROOT.glob(pattern):
            if "node_modules" in str(p) or ".venv" in str(p) or p.suffix == ".d.ts":
                continue
            total += count_suppressions(p)
    return total


def main() -> int:
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"count": 0}
    current = scan()
    allowed = baseline["count"]
    if current > allowed:
        print(f"BLOCKED: Lint suppressions increased ({allowed} → {current}). Fix before committing.")
        return 1
    if current < allowed:
        baseline["count"] = current
        BASELINE.write_text(json.dumps(baseline, indent=2) + "\n")
        print(f"Ratchet improved: {allowed} → {current}. Baseline updated.")
    else:
        print(f"Lint suppressions: {current} (baseline {allowed}). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
