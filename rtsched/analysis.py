"""Analysis functions: hyperperiod, busy period, S_n, response times.

Each function cites the theorem it implements (curriculum guide numbering).
They take a plain list of tasks, so they also work on the subset of tasks
assigned to one core after partitioning.
"""

import math

from rtsched.model import Task

def ceil_div(a: int, b: int) -> int:
    """Ceiling of a / b for integers, with b > 0, computed without floats."""

    # -(-a // b): Python's // rounds down, toward −∞. Negating a, rounding down
    # and negating back gives the ceiling. For example, 7/2: -7 // 2 = -4, so the result is 4.

    return -(-a // b)

def hyperperiod(tasks: list[Task]) -> int:
    """P = lcm(T_1, ..., T_n).

    The hyperperiod is the length after which the release pattern repeats.
    It bounds the feasibility intervals of asynchronous systems:
    [0, S_n + P) for FTP (Th. 45) and [0, O_max + 2P) for EDF (Cor. 63).
    """
    return math.lcm(*(task.period for task in tasks)) # returns the least common multiple of the periods of all tasks

def busy_period(tasks: list[Task]) -> int:
    """Length of the first synchronous busy period.

    Smallest positive solution of w = sum_i ceil(w / T_i) * C_i, found by
    iterating from w_0 = sum_i C_i until w stops changing. This is lambda_n
    for FTP schedulers (Th. 40) and L for EDF (Th. 58): both are the first
    idle point of the synchronous schedule, so the value is the same.

    Requires U <= 1. Then w never decreases, stays an integer and is at most
    P (the processor is idle at some point before P), so the loop ends.
    """
    if sum(task.utilization() for task in tasks) > 1:
        raise ValueError("busy period is only bounded when U <= 1")

    w = sum(task.wcet for task in tasks)
    while True:
        next_w = sum(ceil_div(w, task.period) * task.wcet for task in tasks)
        if next_w == w:
            return w
        w = next_w

def s_n(tasks: list[Task]) -> int:
    """S_n of Th. 45, for tasks given in decreasing priority order.

    S_1 = O_1 and S_i = O_i + ceil((S_{i-1} - O_i)^+ / T_i) * T_i, with
    x^+ = max(x, 0). S_i is the first release of tau_i at or after S_{i-1}.
    For asynchronous constrained-deadline systems under FTP, the schedule is
    feasible if it is feasible up to S_n + P, and then periodic from S_n
    with period P, so [0, S_n + P) is a feasibility interval (Cor. 46).
    """
    s = tasks[0].offset
    for task in tasks[1:]:
        s = task.offset + ceil_div(max(s - task.offset, 0), task.period) * task.period
    return s

def response_times(tasks: list[Task]) -> list[int | None]:
    """Worst-case response time of each task, for tasks given in decreasing
    priority order (synchronous, constrained deadlines).

    r_i is the smallest positive solution of
    r_i = C_i + sum_{j < i} ceil(r_i / T_j) * C_j (Eq. 3.1), found by the
    fixed-point iteration of Eq. 3.2 from w_0 = C_i. The iteration stops when
    w_{k+1} = w_k (exact value) or when w_k > D_i (the deadline is missed and
    the exact value is not needed): that task gets None.
    By Th. 29 the system is FTP-schedulable iff r_i <= D_i for every i,
    that is iff no entry is None.
    """
    result = []
    for i, task in enumerate(tasks):
        higher = tasks[:i]
        w = task.wcet
        while True:
            if w > task.deadline:
                result.append(None)
                break
            next_w = task.wcet + sum(ceil_div(w, hp.period) * hp.wcet for hp in higher)
            if next_w == w:
                result.append(w)
                break
            w = next_w
    return result

def liu_layland_bound(n: int) -> float:
    """n(2^(1/n) - 1), the RM utilization bound of Th. 33.

    A synchronous set of n implicit-deadline periodic tasks is RM-schedulable
    if U <= n(2^(1/n) - 1). The test is sufficient only: above the bound the
    set may still be schedulable. As n grows the bound tends to ln 2 = 0.69
    (Cor. 34).
    """
    return n * (2 ** (1 / n) - 1)
