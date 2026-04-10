#!/usr/bin/env python3
"""Coverage fortress: per-file coverage ratchet.

Reads a JSON coverage report (pytest-cov or vitest) and compares each
file's coverage to the per-file baseline. Regressions beyond ±0.2%
tolerance are blocked. New files must meet 80% floor.

Designed for CI (requires a coverage report to exist). Not a pre-commit hook.

Usage:
  pytest --cov --cov-report=json:coverage.json
  python scripts/governance/check_per_file_baseline.py coverage.json

Exit 0 = OK, Exit 1 = regression detected.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".memory-layer/baselines/coverage.json"
TOLERANCE = 0.2
NEW_FILE_FLOOR = 80.0


def load_pytest_coverage(report_path: pathlib.Path) -> dict[str, float]:
    """Extract per-file line coverage % from pytest-cov JSON report."""
    data = json.loads(report_path.read_text())
    result: dict[str, float] = {}
    for filepath, info in data.get("files", {}).items():
        summary = info.get("summary", {})
        pct = summary.get("percent_covered", 0.0)
        result[filepath] = round(pct, 2)
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_per_file_baseline.py <coverage-report.json>")
        return 1
    report = pathlib.Path(sys.argv[1])
    if not report.exists():
        print(f"Coverage report not found: {report}")
        return 1

    current = load_pytest_coverage(report)
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"files": {}}
    baseline_files: dict[str, float] = baseline.get("files", {})

    regressions: list[str] = []
    updated = False

    for filepath, pct in current.items():
        if filepath in baseline_files:
            allowed = baseline_files[filepath] - TOLERANCE
            if pct < allowed:
                regressions.append(
                    f"  {filepath}: {pct:.1f}% (baseline {baseline_files[filepath]:.1f}%, "
                    f"min {allowed:.1f}%)"
                )
            elif pct > baseline_files[filepath]:
                baseline_files[filepath] = pct
                updated = True
        else:
            # New file
            if pct < NEW_FILE_FLOOR:
                regressions.append(f"  {filepath}: {pct:.1f}% (new file floor {NEW_FILE_FLOOR}%)")
            baseline_files[filepath] = pct
            updated = True

    if regressions:
        print("BLOCKED: Coverage regressions detected:")
        print("\n".join(regressions))
        return 1

    if updated:
        baseline["files"] = baseline_files
        BASELINE.write_text(json.dumps(baseline, indent=2) + "\n")
        print("Coverage fortress: baselines updated (improvements locked in).")
    else:
        print("Coverage fortress: all files at or above baseline. OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
