#!/usr/bin/env python3
"""Iron Dome ratchet: type-hole detection.

Counts ``# type: ignore`` in Python files and ``as any`` in TypeScript files.
Baseline in .memory-layer/baselines/type-holes.json — ratchet only goes DOWN.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".memory-layer/baselines/type-holes.json"

PY_PATTERN = re.compile(r"#\s*type:\s*ignore")
TS_PATTERN = re.compile(r"\bas\s+any\b")


def count_holes(path: pathlib.Path) -> int:
    text = path.read_text(errors="replace")
    pat = PY_PATTERN if path.suffix == ".py" else TS_PATTERN
    return len(pat.findall(text))


def scan() -> int:
    total = 0
    for pattern in ("backend/**/*.py", "frontend/src/**/*.ts"):
        for p in ROOT.glob(pattern):
            if "node_modules" in str(p) or ".venv" in str(p) or p.suffix == ".d.ts":
                continue
            total += count_holes(p)
    return total


def main() -> int:
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"count": 0}
    current = scan()
    allowed = baseline["count"]
    if current > allowed:
        print(f"BLOCKED: Type holes increased ({allowed} → {current}). Fix before committing.")
        return 1
    if current < allowed:
        baseline["count"] = current
        BASELINE.write_text(json.dumps(baseline, indent=2) + "\n")
        print(f"Ratchet improved: {allowed} → {current}. Baseline updated.")
    else:
        print(f"Type holes: {current} (baseline {allowed}). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
