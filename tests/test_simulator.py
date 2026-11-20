"""Tests for the event-driven simulator."""

from rtsched.feasibility import feasibility_interval
from rtsched.model import Task
from rtsched.schedulers import EDF, RM
from rtsched.simulator import simulate


def tasks(*params):
    """Build a list of tasks from (offset, wcet, deadline, period) tuples."""
    return [Task(i, *p) for i, p in enumerate(params)]


def miss(job):
    """(task index, release, deadline, remaining) of a missed job, or None."""
    return None if job is None else (job.task.index, job.release, job.deadline, job.remaining)


SYSTEM_30 = tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 15, 15))       # p. 28, r_3 = 15
SYSTEM_47 = tasks((0, 7, 10, 10), (0, 1, 16, 16), (4, 3, 15, 15))     # p. 36


def test_system_30_meets_every_deadline():
    # tau3 finishes exactly at its deadline 15
    assert simulate(SYSTEM_30, RM(), 0, 15) is None


def test_system_30_with_shorter_deadline_misses():
    # D_3 = 14 < r_3 = 15: the first job of tau3 is 1 unit short at 14
    ts = tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 14, 15))
    assert miss(simulate(ts, RM(), 0, 14)) == (2, 0, 14, 1)


def test_finishing_at_the_deadline_is_not_a_miss():
    assert simulate(tasks((0, 3, 3, 5)), RM(), 0, 5) is None


def test_rm_misses_where_edf_does_not():
    # U = 1: RM runs tau0 at 0-2 and 4-6, tau1 gets only 2 of 3 units before 6
    ts = tasks((0, 2, 4, 4), (0, 3, 6, 6))
    assert miss(simulate(ts, RM(), *feasibility_interval(ts, RM()))) == (1, 0, 6, 1)
    assert simulate(ts, EDF(), *feasibility_interval(ts, EDF())) is None


def test_two_active_jobs_of_one_task_run_fifo():
    # D_1 = 8 > T_1 = 6: at t = 6 the first job of tau1 still needs 1 unit
    # when the second is released; the older one runs first and meets 8
    ts = tasks((0, 2, 4, 4), (0, 3, 8, 6))
    assert simulate(ts, RM(), *feasibility_interval(ts, RM())) is None


def test_deadline_after_the_interval_is_checked():
    # interval [0, 1): tau1's job is released at 0, runs 1-3, deadline 2
    ts = tasks((0, 1, 2, 2), (0, 2, 2, 10))
    assert miss(simulate(ts, RM(), 0, 1)) == (1, 0, 2, 1)


def test_idle_until_first_release():
    assert simulate(tasks((5, 1, 2, 10)), RM(), 0, 10) is None


def test_system_47_rm_misses_edf_does_not():
    # RM order tau1, tau3, tau2: tau2 gets no CPU before its deadline 16
    assert miss(simulate(SYSTEM_47, RM(), *feasibility_interval(SYSTEM_47, RM()))) == (1, 0, 16, 1)
    assert simulate(SYSTEM_47, EDF(), *feasibility_interval(SYSTEM_47, EDF())) is None
