#!/usr/bin/env python3
"""Iron Dome: Silent catch detection.

Scans Python files for bare ``except:`` / ``except Exception:`` blocks with
empty bodies, and TypeScript files for empty ``catch {}`` blocks.

Baseline in .memory-layer/baselines/silent-catches.json — ratchet only goes DOWN.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".memory-layer/baselines/silent-catches.json"

PY_PATTERN = re.compile(
    r"except\s*(?:\w+\s*)?:\s*\n\s*(?:pass|\.\.\.)\s*$", re.MULTILINE
)
TS_PATTERN = re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.MULTILINE)


def count_silent(path: pathlib.Path) -> int:
    text = path.read_text(errors="replace")
    if path.suffix == ".py":
        return len(PY_PATTERN.findall(text))
    if path.suffix == ".ts":
        return len(TS_PATTERN.findall(text))
    return 0


def scan() -> int:
    total = 0
    for pattern in ("backend/**/*.py", "frontend/src/**/*.ts"):
        for p in ROOT.glob(pattern):
            if "node_modules" in str(p) or ".venv" in str(p):
                continue
            total += count_silent(p)
    return total


def main() -> int:
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"count": 0}
    current = scan()
    allowed = baseline["count"]
    if current > allowed:
        print(f"BLOCKED: Silent catches increased ({allowed} → {current}). Fix before committing.")
        return 1
    if current < allowed:
        baseline["count"] = current
        BASELINE.write_text(json.dumps(baseline, indent=2) + "\n")
        print(f"Ratchet improved: {allowed} → {current}. Baseline updated.")
    else:
        print(f"Silent catches: {current} (baseline {allowed}). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
