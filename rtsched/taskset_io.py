"""Reading a task set file: one task per line, `offset;wcet;deadline;period` (section 3.1 of the project description)."""

from rtsched.model import Task, TaskSet


class InvalidTaskFile(Exception):
    """The file is missing or does not follow the expected format."""


def parse_line(line: str, line_number: int, index: int) -> Task:
    """Turn one line such as `70;10;50;50` into a Task."""
    fields = line.split(";")
    if len(fields) != 4:
        raise InvalidTaskFile(
            f"line {line_number}: expected 4 values offset;wcet;deadline;period, got {len(fields)}"
        )
    try:
        offset, wcet, deadline, period = (int(field) for field in fields)
    except ValueError:
        raise InvalidTaskFile(f"line {line_number}: values must be integers: {line!r}")

    if offset < 0:
        raise InvalidTaskFile(f"line {line_number}: the offset must be >= 0")
    if wcet <= 0 or deadline <= 0 or period <= 0:
        raise InvalidTaskFile(f"line {line_number}: wcet, deadline and period must be > 0")

    return Task(index=index, offset=offset, wcet=wcet, deadline=deadline, period=period)


def read_taskset(path: str) -> TaskSet:
    """Read the whole file. Empty lines are skipped."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            lines = file.read().splitlines()
    except OSError as error:
        raise InvalidTaskFile(f"cannot read {path}: {error.strerror}")

    tasks = []
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line:
            tasks.append(parse_line(line, line_number, index=len(tasks)))

    if not tasks:
        raise InvalidTaskFile(f"{path} contains no task")
    return TaskSet(tasks)
