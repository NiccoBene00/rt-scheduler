"""Tests for the analysis functions, against the curriculum guide's examples."""

import pytest

from rtsched.analysis import busy_period, ceil_div, hyperperiod, liu_layland_bound, response_times, s_n
from rtsched.model import Task


def tasks(*params):
    """Build a list of tasks from (offset, wcet, deadline, period) tuples,
    in the given order (= decreasing priority where the order matters)."""
    return [Task(i, *p) for i, p in enumerate(params)]


# Curriculum guide examples
SYSTEM_30 = tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 15, 15))                      # p. 28
SYSTEM_47 = tasks((0, 7, 10, 10), (0, 1, 16, 16), (4, 3, 15, 15))                    # p. 36
SYSTEM_108 = tasks((0, 1, 5, 5), (0, 2, 8, 8), (0, 1, 10, 10), (0, 5, 20, 20))      # p. 111, RM order
SYSTEM_110_DM = tasks((0, 1, 3, 10), (0, 2, 4, 8), (0, 1, 5, 5), (0, 5, 15, 20))    # p. 112, DM order: tau3, tau2, tau1, tau4


# --- ceil_div ------------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [(7, 2, 4), (6, 2, 3), (0, 5, 0), (1, 5, 1)])
def test_ceil_div(a, b, expected):
    assert ceil_div(a, b) == expected


# --- hyperperiod -----------------------------------------------------------------

def test_hyperperiod_system_47():
    assert hyperperiod(SYSTEM_47) == 240


def test_hyperperiod_single_task():
    assert hyperperiod(tasks((0, 1, 7, 7))) == 7


# --- busy_period -----------------------------------------------------------------

def test_busy_period():
    # 6 -> 7 -> 9 -> 10 -> 10
    assert busy_period(tasks((0, 1, 4, 4), (0, 2, 6, 6), (0, 3, 10, 10))) == 10

# (C, T) = (1, 2), (1, 4), (1, 4) gives U = 1/2 + 1/4 + 1/4 = 1. The iteration is 3 → 2+1+1 = 4 → 2+1+1 = 4, so the result is 4 = P.
# That checks the boundary case U = 1, where the Fraction comparison matters.
def test_busy_period_full_utilization():
    # U = 1: the processor is never idle before P = 2
    assert busy_period(tasks((0, 1, 2, 2), (0, 1, 4, 4), (0, 1, 4, 4))) == 4

# U = 3/4 + 2/4 > 1.
def test_busy_period_rejects_overload():
    with pytest.raises(ValueError):
        busy_period(tasks((0, 3, 4, 4), (0, 2, 4, 4)))


# --- s_n -------------------------------------------------------------------------

def test_s_n_system_47():
    # S_1 = 0, S_2 = 0, S_3 = 4: feasibility interval [0, 244)
    assert s_n(SYSTEM_47) == 4
    assert s_n(SYSTEM_47) + hyperperiod(SYSTEM_47) == 244


def test_s_n_skips_whole_periods():
    # S_1 = 0, S_2 = 7 (released after S_1), S_3 = first release of tau3 (2, 6, 10, ...) at or after 7
    assert s_n(tasks((0, 1, 10, 10), (7, 1, 5, 5), (2, 1, 4, 4))) == 10


# --- response_times --------------------------------------------------------------

def test_rta_system_30():
    # r_3 = 5 + 2*2 + 2*3 = 15 (Figure 3.2)
    assert response_times(SYSTEM_30) == [2, 5, 15]


def test_rta_system_108_rm():
    assert response_times(SYSTEM_108) == [1, 3, 4, 14]


def test_rta_system_110_dm():
    assert response_times(SYSTEM_110_DM) == [1, 3, 4, 14]


def test_rta_deadline_miss():
    # System 30 with D_3 = 14 < r_3 = 15
    assert response_times(tasks((0, 2, 8, 8), (0, 3, 11, 11), (0, 5, 14, 15))) == [2, 5, None]


def test_rta_wcet_above_deadline():
    assert response_times(tasks((0, 3, 2, 10))) == [None]


# --- liu_layland_bound -----------------------------------------------------------

def test_liu_layland_values():
    assert [round(liu_layland_bound(n), 3) for n in (1, 2, 3, 4)] == [1.0, 0.828, 0.78, 0.757]


def test_liu_layland_is_only_sufficient():
    # System 108: U = 0.8 > bound(4), yet RTA shows it is RM-schedulable
    u = sum(task.utilization() for task in SYSTEM_108)
    assert u > liu_layland_bound(4)
    assert None not in response_times(SYSTEM_108)
