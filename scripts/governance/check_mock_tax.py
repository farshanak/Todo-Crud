#!/usr/bin/env python3
"""Rising Tide: mock tax enforcer (2x rule).

If a test file uses mocking (mock, patch, Mock, vi.fn, vi.mock) AND its
line count is >2x the source file's line count, the test is rejected.
Integration tests (tests/integration/) are exempt — the 2x rule targets
bloated *unit* tests that mock too heavily.

Exit 0 = OK, Exit 1 = blocked.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAX_RATIO = 2.0

MOCK_MARKERS_PY = re.compile(r"\bMock\b|\bpatch\b|\bcreate_autospec\b")
MOCK_MARKERS_TS = re.compile(r"\bvi\.mock\(|\bjest\.mock\(")


def loc(path: pathlib.Path) -> int:
    return sum(1 for line in path.read_text(errors="replace").splitlines() if line.strip())


def check_python() -> list[str]:
    violations = []
    for test_file in ROOT.glob("backend/tests/unit/**/*.py"):
        if test_file.name == "__init__.py" or test_file.name == "conftest.py":
            continue
        text = test_file.read_text(errors="replace")
        if not MOCK_MARKERS_PY.search(text):
            continue
        # Derive source file name: test_foo.py -> foo.py
        src_name = test_file.name.removeprefix("test_") if test_file.name.startswith("test_") else None
        if not src_name:
            continue
        candidates = list(ROOT.glob(f"backend/{src_name}")) + list(ROOT.glob(f"backend/**/{src_name}"))
        if not candidates:
            continue
        src_loc = loc(candidates[0])
        if src_loc == 0:
            continue
        test_loc = loc(test_file)
        ratio = test_loc / src_loc
        if ratio > MAX_RATIO:
            violations.append(f"  {test_file.relative_to(ROOT)}: {test_loc} LOC / {src_loc} src = {ratio:.1f}x (max {MAX_RATIO}x)")
    return violations


def check_typescript() -> list[str]:
    violations = []
    # Only check unit-level tests (not integration, not behavioral)
    for test_file in ROOT.glob("frontend/src/**/*.test.ts"):
        text = test_file.read_text(errors="replace")
        if not MOCK_MARKERS_TS.search(text):
            continue
        src_name = test_file.name.replace(".test.ts", ".ts")
        src_path = test_file.parent / src_name
        if not src_path.exists():
            continue
        src_loc = loc(src_path)
        if src_loc == 0:
            continue
        test_loc = loc(test_file)
        ratio = test_loc / src_loc
        if ratio > MAX_RATIO:
            violations.append(f"  {test_file.relative_to(ROOT)}: {test_loc} LOC / {src_loc} src = {ratio:.1f}x (max {MAX_RATIO}x)")
    return violations


def main() -> int:
    violations = check_python() + check_typescript()
    if violations:
        print("BLOCKED: Mock Tax exceeded (test LOC > 2x source LOC with mocking):")
        print("\n".join(violations))
        print("Solution: Delete the unit test and write an integration test instead.")
        return 1
    print("Mock tax: all mocked tests within 2x ratio. OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
