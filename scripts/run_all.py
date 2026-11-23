"""Run the program on many task sets.

    python scripts/run_all.py <folder> [-m N] [-H ff|bf|nf|wf] [-s du|iu]
        Exit code of every task file under <folder> with rm, dm and edf,
        then how many files give each code, per sub-folder (for the report).

    python scripts/run_all.py --check <expected.csv>
        Run every row of the CSV (file,algorithm,cores,heuristic,sort,expected)
        and list the rows whose exit code differs. Exits 1 if any row differs.
"""

import argparse
import contextlib
import csv
import io
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # find rtsched from scripts/
from rtsched.cli import main  # noqa: E402

ALGORITHMS = ("rm", "dm", "edf")
CODES = range(5)


def run(path: Path, algorithm: str, cores: int, heuristic: str, sort: str) -> int:
    """Exit code of the program on one file, with its output hidden."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main([str(path), "-a", algorithm, "-m", str(cores), "-h", heuristic, "-s", sort])


def table(folder: Path, cores: int, heuristic: str, sort: str) -> None:
    """Print the exit code of every file with each algorithm, then the counts."""
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix != ".csv")
    counts = Counter()
    print(f"{'file':<40}" + "".join(f"{a:>5}" for a in ALGORITHMS))
    for path in files:
        group = path.parent.relative_to(folder).as_posix()
        codes = [run(path, a, cores, heuristic, sort) for a in ALGORITHMS]
        for algorithm, code in zip(ALGORITHMS, codes):
            counts[group, algorithm, code] += 1
        print(f"{path.relative_to(folder).as_posix():<40}" + "".join(f"{c:>5}" for c in codes))

    print(f"\n{'folder':<30}{'alg':>5}" + "".join(f"{c:>5}" for c in CODES))
    for group in sorted({g for g, _, _ in counts}):
        for algorithm in ALGORITHMS:
            print(f"{group:<30}{algorithm:>5}" + "".join(f"{counts[group, algorithm, c]:>5}" for c in CODES))


def check(expected_csv: Path) -> int:
    """Run every row of the CSV; print the differences; 0 if none, else 1."""
    with open(expected_csv, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    wrong = 0
    for row in rows:
        code = run(expected_csv.parent / row["file"], row["algorithm"], int(row["cores"]),
                   row["heuristic"], row["sort"])
        if code != int(row["expected"]):
            wrong += 1
            print(f"{row['file']} -a {row['algorithm']} -m {row['cores']} -h {row['heuristic']} "
                  f"-s {row['sort']}: expected {row['expected']}, got {code}")
    print(f"{len(rows) - wrong}/{len(rows)} rows as expected")
    return 1 if wrong else 0


def main_script() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", nargs="?", type=Path, help="folder with task set files")
    parser.add_argument("--check", type=Path, metavar="CSV", help="expected exit codes to compare with")
    parser.add_argument("-m", dest="cores", type=int, default=1)
    parser.add_argument("-H", dest="heuristic", default="ff", choices=["ff", "bf", "nf", "wf"])
    parser.add_argument("-s", dest="sort", default="du", choices=["du", "iu"])
    args = parser.parse_args()

    start = time.perf_counter()
    if args.check:
        result = check(args.check)
    elif args.folder:
        table(args.folder, args.cores, args.heuristic, args.sort)
        result = 0
    else:
        parser.error("give a folder or --check CSV")
    print(f"done in {time.perf_counter() - start:.1f} s")
    return result


if __name__ == "__main__":
    sys.exit(main_script())
