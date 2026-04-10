#!/usr/bin/env python3
"""SRP guardrails: file and function size limits.

- File: warn > 300 LOC, block > 600 LOC (source, not tests)
- Function: block > 50 LOC
- Amnesty: existing violations in .memory-layer/baselines/guardrails.json

Exit 0 = OK, Exit 1 = blocked.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".memory-layer/baselines/guardrails.json"

MAX_FILE_LOC = 600
WARN_FILE_LOC = 300
MAX_FUNC_LOC = 50

PY_FUNC = re.compile(r"^(?:    )*(?:async\s+)?def\s+(\w+)", re.MULTILINE)
TS_FUNC = re.compile(
    r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|"
    r"(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\(",
    re.MULTILINE,
)


def loc(path: pathlib.Path) -> int:
    return sum(1 for l in path.read_text(errors="replace").splitlines() if l.strip())


def function_lengths(path: pathlib.Path) -> list[tuple[str, int]]:
    """Approximate function lengths by counting lines between def/function declarations."""
    lines = path.read_text(errors="replace").splitlines()
    pat = PY_FUNC if path.suffix == ".py" else TS_FUNC
    funcs: list[tuple[str, int]] = []
    positions: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = pat.match(line)
        if m:
            name = m.group(1) or (m.group(2) if m.lastindex and m.lastindex >= 2 else None)
            if name:
                positions.append((name, i))
    for idx, (name, start) in enumerate(positions):
        end = positions[idx + 1][1] if idx + 1 < len(positions) else len(lines)
        length = sum(1 for l in lines[start:end] if l.strip())
        funcs.append((name, length))
    return funcs


def scan() -> tuple[list[str], list[str]]:
    amnesty = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"amnesty_files": []}
    amnesty_set = set(amnesty.get("amnesty_files", []))
    errors: list[str] = []
    warnings: list[str] = []
    for pattern in ("backend/**/*.py", "frontend/src/**/*.ts"):
        for p in ROOT.glob(pattern):
            if "node_modules" in str(p) or ".venv" in str(p) or "test" in str(p).lower():
                continue
            rel = str(p.relative_to(ROOT))
            file_loc = loc(p)
            if file_loc > MAX_FILE_LOC and rel not in amnesty_set:
                errors.append(f"  {rel}: {file_loc} LOC (max {MAX_FILE_LOC})")
            elif file_loc > WARN_FILE_LOC:
                warnings.append(f"  {rel}: {file_loc} LOC (warn > {WARN_FILE_LOC})")
            for fname, flen in function_lengths(p):
                if flen > MAX_FUNC_LOC:
                    errors.append(f"  {rel}:{fname}(): {flen} LOC (max {MAX_FUNC_LOC})")
    return errors, warnings


def main() -> int:
    errors, warnings = scan()
    if warnings:
        for w in warnings:
            print(f"WARN: {w}")
    if errors:
        print("BLOCKED: SRP guardrails violated:")
        for e in errors:
            print(e)
        return 1
    print("SRP guardrails: all files and functions within limits. OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
