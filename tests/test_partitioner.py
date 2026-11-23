"""Tests for the partitioner (bin-packing heuristics, capacity 1 per core)."""

import pytest

from rtsched.model import Task
from rtsched.partitioner import partition, sort_by_utilization


def tasks_with_utilization(*wcets, period=10):
    """Implicit-deadline tasks with U_i = C_i / period, in the given order."""
    return [Task(i, 0, c, period, period) for i, c in enumerate(wcets)]


def indices(cores):
    """Task indices on each core, or None if partitioning failed."""
    return None if cores is None else [[task.index for task in core] for core in cores]


# U = 0.1, 0.1, 0.4, 0.5, 0.7 on 3 cores: the four heuristics give four partitions
EXAMPLE = tasks_with_utilization(1, 1, 4, 5, 7)


def test_sort_by_utilization():
    ts = tasks_with_utilization(1, 1, 4, 5, 7)
    assert [t.index for t in sort_by_utilization(ts, "du")] == [4, 3, 2, 0, 1]
    assert [t.index for t in sort_by_utilization(ts, "iu")] == [0, 1, 2, 3, 4]


@pytest.mark.parametrize("heuristic, expected", [
    # du order: 0.7, 0.5, 0.4, 0.1 (tau0), 0.1 (tau1)
    ("ff", [[0, 1, 4], [2, 3], []]),    # first core that fits
    ("bf", [[1, 4], [0, 2, 3], []]),    # 0.4 and the first 0.1 go to the fullest core
    ("wf", [[4], [1, 3], [0, 2]]),      # always the emptiest core
    ("nf", [[4], [0, 2, 3], [1]]),      # the last 0.1 does not fit core 1: core 2, never back
])
def test_heuristics_differ(heuristic, expected):
    assert indices(partition(EXAMPLE, 3, heuristic, "du")) == expected


def test_next_fit_fails_where_first_fit_succeeds():
    # du order 0.6, 0.5, 0.5, 0.4 on 2 cores: FF puts 0.4 back on core 0, NF cannot
    ts = tasks_with_utilization(5, 6, 4, 5)
    assert indices(partition(ts, 2, "ff", "du")) == [[1, 2], [0, 3]]
    assert partition(ts, 2, "nf", "du") is None


def test_exact_capacity_with_fractions():
    # 3 x 1/3 = 1 exactly: fits on one core (a float sum could round above 1)
    ts = tasks_with_utilization(1, 1, 1, period=3)
    assert indices(partition(ts, 1, "ff", "du")) == [[0, 1, 2]]


def test_task_above_one_never_fits():
    ts = [Task(0, 0, 3, 4, 2)]   # U = 3/2
    for heuristic in ("ff", "bf", "wf", "nf"):
        assert partition(ts, 4, heuristic, "du") is None


def test_one_core_fails_iff_total_above_one():
    assert partition(tasks_with_utilization(5, 5), 1, "ff", "du") is not None
    assert partition(tasks_with_utilization(5, 6), 1, "ff", "du") is None
