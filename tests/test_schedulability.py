"""Tests for the decision order on one processor (schedulability.py)."""

from rtsched.exit_codes import (
    NOT_SCHEDULABLE_ANALYSIS,
    NOT_SCHEDULABLE_SIMULATION,
    SCHEDULABLE,
    UNSUPPORTED,
)
from rtsched.model import Task
from rtsched.schedulability import check_schedulability
from rtsched.schedulers import DM, EDF, RM


def tasks(*params):
    """Build a list of tasks from (offset, wcet, deadline, period) tuples."""
    return [Task(i, *p) for i, p in enumerate(params)]


SYSTEM_30 = tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 15, 15))       # p. 28
SYSTEM_47 = tasks((0, 7, 10, 10), (0, 1, 16, 16), (4, 3, 15, 15))     # p. 36


# --- 1. unsupported ----------------------------------------------------------------

def test_unsupported():
    code, reason = check_schedulability(tasks((0, 1, 30, 10), (3, 1, 5, 10)), DM())
    assert code == UNSUPPORTED
    assert "arbitrary deadlines" in reason

# this is the test for which I moved check_supported out of feasibility_interval.
def test_unsupported_comes_before_overload():
    # U = 5/4 > 1, but the combination is unsupported first
    code, _ = check_schedulability(tasks((0, 3, 30, 4), (3, 2, 5, 4)), RM())
    assert code == UNSUPPORTED


# --- 2. necessary conditions -------------------------------------------------------

def test_wcet_above_deadline():
    assert check_schedulability(tasks((0, 3, 2, 10)), EDF()) == (NOT_SCHEDULABLE_ANALYSIS, "tau1: C = 3 > D = 2")


def test_overload():
    assert check_schedulability(tasks((0, 3, 4, 4), (0, 2, 4, 4)), RM()) == (NOT_SCHEDULABLE_ANALYSIS, "U = 5/4 > 1")


# --- 3. tests without simulation ---------------------------------------------------

# system 47 under EDF gives 0 without simulation. Earlier the simulation reached the same answer (None on [0, 484)), so the two methods agree.
def test_edf_implicit_by_utilization():
    # asynchronous too: Cor. 54 does not need a synchronous set
    code, reason = check_schedulability(SYSTEM_47, EDF())
    assert code == SCHEDULABLE
    assert "Cor. 54" in reason


def test_rm_sync_rta_passes():
    assert check_schedulability(SYSTEM_30, RM()) == (SCHEDULABLE, "response times [2, 5, 15] within the deadlines (Th. 29)")


def test_rm_sync_rta_fails_exactly():
    ts = tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 14, 15))
    assert check_schedulability(ts, RM()) == (NOT_SCHEDULABLE_ANALYSIS, "tau3: response time > D = 14 (Th. 29)")


def test_rm_async_passes_by_synchronous_rta():
    code, reason = check_schedulability(tasks((0, 1, 4, 4), (2, 1, 6, 6)), RM())
    assert code == SCHEDULABLE
    assert "Th. 29" in reason


# --- 4. simulation -----------------------------------------------------------------

# this test is the cas for which step 3 can't say "not schedulable" for asynchronous sets.
#  - Released together, τ1 = (2, 4) and τ2 = (3, 6) fail under RM: τ2 gets only 2 units before 6.
#  - With O_2 = 1 there's no bad overlap: τ2 runs 2–4 and 6–7 and finishes exactly at its deadline 7.
#  - The interval is [0, S_2 + P) = [0, 1 + 12).
def test_rm_async_fails_rta_but_passes_simulation():
    # synchronously tau2 misses at 6 (U = 1); with O_2 = 1 it finishes at 7 = its deadline
    ts = tasks((0, 2, 4, 4), (1, 3, 6, 6))
    assert check_schedulability(ts, RM()) == (SCHEDULABLE, "no deadline miss in [0, 13)")


def test_rm_async_misses_in_simulation():
    assert check_schedulability(SYSTEM_47, RM()) == (
        NOT_SCHEDULABLE_SIMULATION, "tau2 misses its deadline at 16 (job released at 0)")


def test_rm_sync_arbitrary_simulated():
    assert check_schedulability(tasks((0, 2, 4, 4), (0, 3, 8, 6)), RM()) == (SCHEDULABLE, "no deadline miss in [0, 12)")


def test_edf_constrained_simulated():
    assert check_schedulability(tasks((0, 1, 3, 4), (0, 2, 5, 6)), EDF()) == (SCHEDULABLE, "no deadline miss in [0, 3)")


def test_edf_constrained_misses_in_simulation():
    # U = 1: tau1 runs 0-2 (deadline 2), tau2 then misses its deadline 3
    assert check_schedulability(tasks((0, 2, 2, 4), (0, 2, 3, 4)), EDF()) == (
        NOT_SCHEDULABLE_SIMULATION, "tau2 misses its deadline at 3 (job released at 0)")
