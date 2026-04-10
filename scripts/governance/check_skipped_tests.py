#!/usr/bin/env python3
"""Test discipline: skipped-test gate.

Ensures ≤5% of tests are marked as skipped (pytest.mark.skip, @skip, .skip,
it.skip, describe.skip, test.skip, xit, xdescribe).

Exit 0 = OK, Exit 1 = blocked.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAX_SKIP_PERCENT = 5.0

PY_SKIP = re.compile(r"@pytest\.mark\.skip|pytest\.skip\(|@unittest\.skip")
PY_TEST = re.compile(r"^\s*(?:async\s+)?def\s+(test_\w+)", re.MULTILINE)
TS_SKIP = re.compile(r"\b(?:it|test|describe)\.skip\b|\bxit\b|\bxdescribe\b")
TS_TEST = re.compile(r"\b(?:it|test)\s*\(", re.MULTILINE)


def scan() -> tuple[int, int]:
    total_tests = 0
    total_skipped = 0
    for p in ROOT.glob("backend/tests/**/*.py"):
        if p.name == "__init__.py" or p.name == "conftest.py":
            continue
        text = p.read_text(errors="replace")
        total_tests += len(PY_TEST.findall(text))
        total_skipped += len(PY_SKIP.findall(text))
    for p in ROOT.glob("frontend/src/**/*.test.ts"):
        text = p.read_text(errors="replace")
        total_tests += len(TS_TEST.findall(text))
        total_skipped += len(TS_SKIP.findall(text))
    return total_tests, total_skipped


def main() -> int:
    total, skipped = scan()
    if total == 0:
        print("No tests found.")
        return 0
    pct = (skipped / total) * 100
    if pct > MAX_SKIP_PERCENT:
        print(f"BLOCKED: {skipped}/{total} tests skipped ({pct:.1f}%, max {MAX_SKIP_PERCENT}%).")
        return 1
    print(f"Skipped tests: {skipped}/{total} ({pct:.1f}%, max {MAX_SKIP_PERCENT}%). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
