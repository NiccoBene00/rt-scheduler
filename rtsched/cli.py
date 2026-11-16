"""Command line: ./project <task_file> -a edf|rm|dm [-m <#cores>] [-h ff|bf|nf|wf] [-s du|iu]

Section 4.1 of the project description.

"""

import argparse
import sys

from rtsched.exit_codes import INVALID_INPUT, SCHEDULABLE
from rtsched.taskset_io import InvalidTaskFile, read_taskset


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
    parser.add_argument("--help", action="help", help="show this help and exit")
    return parser.parse_args(argv)


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

    # TODO (M3-M5): partitioning, feasibility interval, schedulability.
    return SCHEDULABLE


