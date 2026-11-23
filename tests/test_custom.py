"""End-to-end tests: the program on real task set files.

- tasksets/custom/expected.csv: my own task sets with the exit code I
  derived from the curriculum guide.
- The course samples (../../tasksets test/, outside the repo): no expected
  codes are given, so only consistency is checked. Skipped if not found.
"""

import csv
import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from rtsched.cli import main

REPO = Path(__file__).resolve().parent.parent
CUSTOM = REPO / "tasksets" / "custom"
SAMPLES = REPO.parent.parent / "tasksets test" # real samples from the course


def run(path, *options):
    """Exit code of the program, with its output hidden."""
    with redirect_stdout(io.StringIO()):
        return main([str(path), *options])


def expected_rows():
    with open(CUSTOM / "expected.csv", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


@pytest.mark.parametrize("row", expected_rows(), ids=lambda r: "-".join(r[k] for k in ("file", "algorithm", "cores", "heuristic", "sort")))
def test_custom_taskset(row):
    options = ["-a", row["algorithm"], "-m", row["cores"], "-h", row["heuristic"], "-s", row["sort"]]
    assert run(CUSTOM / row["file"], *options) == int(row["expected"])


@pytest.mark.skipif(not SAMPLES.is_dir(), reason="course samples not found")
def test_samples_are_consistent():
    # EDF is optimal on one core (Th. 52): whatever RM or DM schedules, EDF schedules too
    files = sorted(p for p in SAMPLES.rglob("*") if p.is_file())
    assert len(files) == 60
    for path in files:
        codes = {a: run(path, "-a", a) for a in ("rm", "dm", "edf")}
        assert all(code in (0, 2, 3, 4) for code in codes.values()), path
        if codes["rm"] == 0 or codes["dm"] == 0:
            assert codes["edf"] == 0, path
