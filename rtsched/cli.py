"""Command line: ./project <task_file> -a edf|rm|dm [-m <#cores>] [-h ff|bf|nf|wf] [-s du|iu]

Section 4.1 of the project description.

"""

import argparse
import sys
from pathlib import Path

from rtsched.exit_codes import (
    INVALID_INPUT,
    NOT_SCHEDULABLE_ANALYSIS,
    NOT_SCHEDULABLE_SIMULATION,
    PARTITION_FAILED,
    SCHEDULABLE,
    UNSUPPORTED,
)
from rtsched.partitioner import partition
from rtsched.schedulability import check_schedulability
from rtsched.schedulers import get_scheduler
from rtsched.taskset_io import InvalidTaskFile, read_taskset

# What each exit code means, printed before the reason.
VERDICTS = {
    SCHEDULABLE: "schedulable",
    UNSUPPORTED: "unsupported",
    NOT_SCHEDULABLE_ANALYSIS: "not schedulable (without simulation)",
    NOT_SCHEDULABLE_SIMULATION: "not schedulable (simulation)",
}

class ArgumentParser(argparse.ArgumentParser):
    """argparse generally exits with code 2 on bad arguments, which would mean
    'unsupported combination' here. We will have a conflict of notation.
    Exit with INVALID_INPUT instead."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        sys.exit(INVALID_INPUT)


def positive_int(text: str) -> int:
    """Type check for -m: a strictly positive integer."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not an integer")
    if value <= 0:
        raise argparse.ArgumentTypeError("the number of cores must be > 0")
    return value


def parse_args(argv):
    # add_help=False: -h is the heuristic flag, so argparse's own -h must go.
    parser = ArgumentParser(
        prog="project",
        description="RM, DM and EDF schedulability for periodic task sets.",
        add_help=False,
    )
    parser.add_argument("task_file", help="file with one task per line: offset;wcet;deadline;period")
    parser.add_argument("-a", dest="algorithm", required=True, choices=["edf", "rm", "dm"],
                        help="scheduling algorithm")
    parser.add_argument("-m", dest="cores", type=positive_int, default=1,
                        help="number of identical cores (default 1)")
    parser.add_argument("-h", dest="heuristic", choices=["ff", "bf", "nf", "wf"], default="ff",
                        help="partitioning heuristic (default ff)")
    parser.add_argument("-s", dest="sort", choices=["du", "iu"], default="du",
                        help="sort by decreasing or increasing utilization (default du)")
    parser.add_argument("--plot", metavar="FILE", help="bonus: save a Gantt chart of each core to FILE (PNG)")
    parser.add_argument("--help", action="help", help="show this help and exit")
    return parser.parse_args(argv)

def gantt_path(plot: str, core: int, cores: int) -> str:
    """FILE itself for one core; FILE-coreK.png for core K of several."""
    if cores == 1:
        return plot
    path = Path(plot)
    return str(path.with_name(f"{path.stem}-core{core + 1}{path.suffix}"))


def main(argv=None) -> int:
    """Run the program and return its exit code."""
    args = parse_args(argv)

    try:
        taskset = read_taskset(args.task_file)
    except InvalidTaskFile as error:
        print(f"error: {error}", file=sys.stderr)
        return INVALID_INPUT

    print(f"{len(taskset.tasks)} tasks, {taskset.describe()}, U = {float(taskset.utilization()):.3f}")
    print(f"algorithm {args.algorithm}, {args.cores} core(s), heuristic {args.heuristic}, sort {args.sort}")

    if args.cores == 1:
        cores = [taskset.tasks]  # one core: nothing to partition
    else:
        cores = partition(taskset.tasks, args.cores, args.heuristic, args.sort)
        if cores is None:
            print(f"partitioning failed: some task fits on no core ({args.heuristic}, {args.sort})")
            return PARTITION_FAILED

    scheduler = get_scheduler(args.algorithm)
    for k, core_tasks in enumerate(cores):
        if not core_tasks:
            continue
        code, reason = check_schedulability(core_tasks, scheduler)
        names = ", ".join(f"tau{task.index + 1}" for task in core_tasks)
        print(f"core {k + 1} ({names}): {VERDICTS[code]}: {reason}")
        if args.plot and code != UNSUPPORTED:
            from rtsched.visualization import plot_core  # matplotlib is only needed with --plot
            path = gantt_path(args.plot, k, len(cores))
            plot_core(core_tasks, scheduler, path, f"{Path(args.task_file).name}, core {k + 1}")
            print(f"  Gantt chart saved to {path}")
        if code != SCHEDULABLE:
            return code
    return SCHEDULABLE
