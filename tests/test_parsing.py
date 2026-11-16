"""Tests for reading task files (taskset_io) and classifying task sets (model)."""

from fractions import Fraction

import pytest

from rtsched.model import ARBITRARY, CONSTRAINED, IMPLICIT, Job, Task, TaskSet
from rtsched.taskset_io import InvalidTaskFile, read_taskset


def write(tmp_path, text):
    """Write `text` to a temporary file and return its path."""
    path = tmp_path / "taskset"
    path.write_text(text, encoding="utf-8")
    return str(path)


def make(*tasks):
    """Build a TaskSet from (offset, wcet, deadline, period) tuples."""
    return TaskSet([Task(i, *t) for i, t in enumerate(tasks)])


# --- reading files -----------------------------------------------------------

def test_reads_statement_example(tmp_path):
    # Listing 1 of the statement
    taskset = read_taskset(write(tmp_path, "70;10;50;50\n0;20;120;80\n0;10;40;100\n20;50;200;200\n"))
    assert len(taskset.tasks) == 4
    assert taskset.tasks[1] == Task(index=1, offset=0, wcet=20, deadline=120, period=80)


def test_blank_lines_crlf_and_bom(tmp_path):
    taskset = read_taskset(write(tmp_path, "\ufeff0;1;5;5\r\n\r\n0;2;8;8\r\n"))
    assert [task.index for task in taskset.tasks] == [0, 1]
    assert taskset.tasks[0].offset == 0


@pytest.mark.parametrize("text", [
    "0;1;5\n",        # 3 values
    "0;1;5;5;1\n",    # 5 values
    "0;x;5;5\n",      # not an integer
    "0;1.5;5;5\n",    # not an integer
    "-1;1;5;5\n",     # negative offset
    "0;0;5;5\n",      # wcet 0
    "0;1;5;0\n",      # period 0
    "",               # no task at all
])
def test_invalid_files(tmp_path, text):
    with pytest.raises(InvalidTaskFile):
        read_taskset(write(tmp_path, text))


def test_missing_file(tmp_path):
    with pytest.raises(InvalidTaskFile):
        read_taskset(str(tmp_path / "does-not-exist"))


def test_wcet_larger_than_deadline_is_valid_input(tmp_path):
    # C > D is not a format error: the analysis will reject it (exit 3)
    taskset = read_taskset(write(tmp_path, "0;6;5;10\n"))
    assert taskset.tasks[0].wcet == 6


# --- classification ----------------------------------------------------------

def test_deadline_types():
    assert make((0, 1, 5, 5), (0, 2, 8, 8)).deadline_type() == IMPLICIT
    assert make((0, 1, 4, 5), (0, 2, 8, 8)).deadline_type() == CONSTRAINED
    assert make((0, 1, 7, 5), (0, 2, 8, 8)).deadline_type() == ARBITRARY


def test_synchronous_or_not():
    assert make((0, 1, 5, 5), (0, 2, 8, 8)).is_synchronous()
    assert make((3, 1, 5, 5), (3, 2, 8, 8)).is_synchronous()   # equal offsets, shifted
    assert not make((0, 1, 5, 5), (2, 2, 8, 8)).is_synchronous()
    assert make((70, 10, 50, 50), (0, 20, 120, 80)).describe() == "asynchronous arbitrary"


def test_utilization_is_exact():
    # with floats 1/3 + 1/3 + 1/3 is not always exactly 1; with Fraction it is
    taskset = make((0, 1, 3, 3), (0, 1, 3, 3), (0, 1, 3, 3))
    assert taskset.utilization() == 1
    assert make((0, 1, 10, 10), (0, 2, 10, 10)).utilization() == Fraction(3, 10)


def test_job_deadline_and_release():
    task = Task(index=0, offset=2, wcet=3, deadline=4, period=10)
    assert task.release_time(0) == 2 and task.release_time(3) == 32
    job = Job(task=task, release=task.release_time(1), remaining=task.wcet)
    assert job.deadline == 16    # 12 + 4
