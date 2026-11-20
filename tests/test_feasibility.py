"""Tests for the schedulers (priority keys) and the feasibility intervals."""

import pytest

from rtsched.analysis import response_times
from rtsched.feasibility import Unsupported, feasibility_interval
from rtsched.model import Job, Task
from rtsched.schedulers import DM, EDF, RM, get_scheduler


def tasks(*params):
    """Build a list of tasks from (offset, wcet, deadline, period) tuples."""
    return [Task(i, *p) for i, p in enumerate(params)]


SYSTEM_47 = tasks((0, 7, 10, 10), (0, 1, 16, 16), (4, 3, 15, 15))                 # p. 36
SYSTEM_110 = tasks((0, 1, 5, 5), (0, 2, 4, 8), (0, 1, 3, 10), (0, 5, 15, 20))     # p. 112, curriculum guide's order


# --- schedulers ------------------------------------------------------------------

def test_get_scheduler():
    assert [type(get_scheduler(n)) for n in ("rm", "dm", "edf")] == [RM, DM, EDF]
    assert RM().fixed_task_priority and DM().fixed_task_priority
    assert not EDF().fixed_task_priority


def test_pick_rm_dm_edf():
    # t = 5: job A of tau0 (released 5, deadline 10), job B of tau1 (released 0, deadline 7)
    t0, t1 = tasks((0, 2, 5, 5), (0, 4, 7, 20))
    a, b = Job(t0, 5, 2), Job(t1, 0, 4)
    assert RM().pick([b, a]) is a
    assert DM().pick([b, a]) is a
    assert EDF().pick([a, b]) is b


def test_pick_fifo_within_a_task():
    # arbitrary deadline: two active jobs of the same task, the older runs first
    (t0,) = tasks((0, 4, 12, 5))
    old, new = Job(t0, 0, 1), Job(t0, 5, 4)
    for scheduler in (RM(), DM(), EDF()):
        assert scheduler.pick([new, old]) is old


def test_ties_go_to_the_first_task():
    t0, t1 = tasks((0, 1, 10, 10), (0, 1, 10, 10))
    assert [t.index for t in RM().sort_tasks([t1, t0])] == [0, 1]
    assert EDF().pick([Job(t1, 0, 1), Job(t0, 0, 1)]).task is t0


def test_dm_order_system_110():
    ordered = DM().sort_tasks(SYSTEM_110)
    assert [t.index for t in ordered] == [2, 1, 0, 3]
    assert response_times(ordered) == [1, 3, 4, 14]


# --- feasibility intervals: synchronous --------------------------------------------

def test_sync_ftp_constrained_dmax_equals_lambda():
    # system 30: lambda_n = 15 = D_max
    assert feasibility_interval(tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 15, 15)), RM()) == (0, 15)


def test_sync_ftp_constrained_lambda_smaller():
    # lambda_n = 2 < D_max = 20
    assert feasibility_interval(tasks((0, 1, 10, 10), (0, 1, 20, 20)), RM()) == (0, 2)


def test_sync_ftp_constrained_dmax_smaller():
    # lambda_n = 4 > D_max = 3
    assert feasibility_interval(tasks((0, 3, 3, 4), (0, 1, 2, 8)), DM()) == (0, 3)


def test_sync_arbitrary_uses_lambda():
    # D_0 = 3 > T_0 = 2: arbitrary, so lambda_n = 6 even though D_max = 4
    ts = tasks((0, 1, 3, 2), (0, 3, 4, 8))
    assert feasibility_interval(ts, RM()) == (0, 6)
    assert feasibility_interval(ts, EDF()) == (0, 6)


def test_sync_shifted_offsets():
    # every offset = 5: the O = 0 interval shifted by 5
    assert feasibility_interval(tasks((5, 3, 3, 4), (5, 1, 2, 8)), DM()) == (5, 8)
    assert feasibility_interval(tasks((5, 1, 4, 4), (5, 2, 6, 6)), EDF()) == (5, 8)


# --- feasibility intervals: asynchronous -------------------------------------------

def test_async_ftp_system_47_rm():
    # RM order is tau1, tau3, tau2 (periods 10, 15, 16), not the guide's tau1, tau2, tau3:
    # S_n = 16 (the guide's 4 is for its own order), P = 240
    assert feasibility_interval(SYSTEM_47, RM()) == (0, 256)


def test_async_edf_system_47():
    # O_max = 4, P = 240
    assert feasibility_interval(SYSTEM_47, EDF()) == (0, 484)


def test_async_edf_arbitrary():
    assert feasibility_interval(tasks((0, 1, 30, 10), (3, 1, 5, 10)), EDF()) == (0, 23)


def test_async_ftp_arbitrary_unsupported():
    with pytest.raises(Unsupported, match="DM"):
        feasibility_interval(tasks((0, 1, 30, 10), (3, 1, 5, 10)), DM())
