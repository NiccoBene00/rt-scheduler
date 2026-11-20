"""Schedulability of a task set on one processor.

1. Unsupported combination -> 2.
2. Some C_i > D_i, or U > 1 -> 3.
3. A test without simulation decides -> 0 (or 3 when the test is exact).
4. Otherwise simulate the feasibility interval -> 0 or 4.
"""

from rtsched.analysis import response_times
from rtsched.exit_codes import (
    NOT_SCHEDULABLE_ANALYSIS,
    NOT_SCHEDULABLE_SIMULATION,
    SCHEDULABLE,
    UNSUPPORTED,
)
from rtsched.feasibility import Unsupported, check_supported, feasibility_interval
from rtsched.model import ARBITRARY, IMPLICIT, Task, TaskSet
from rtsched.schedulers import Scheduler
from rtsched.simulator import simulate


def check_schedulability(tasks: list[Task], scheduler: Scheduler) -> tuple[int, str]:
    """Exit code and a one-line reason for one processor.

    Tests without simulation:
    - EDF, implicit deadlines: feasible iff U <= 1 (Cor. 54), so 0.
    - FTP, constrained deadlines: response times of the synchronous set
      (Th. 29). For a synchronous set the test is exact (0 or 3). For an
      asynchronous set the synchronous release is the worst case (critical
      instant, Lemma 25), so passing gives 0; failing decides nothing and
      the set is simulated.
    """
    taskset = TaskSet(tasks)

    try:
        check_supported(tasks, scheduler)
    except Unsupported as error:
        return UNSUPPORTED, str(error)

    for task in tasks:
        if task.wcet > task.deadline:
            return NOT_SCHEDULABLE_ANALYSIS, f"tau{task.index + 1}: C = {task.wcet} > D = {task.deadline}"
    u = taskset.utilization()
    if u > 1:
        return NOT_SCHEDULABLE_ANALYSIS, f"U = {u} > 1"

    deadline_type = taskset.deadline_type()
    if not scheduler.fixed_task_priority and deadline_type == IMPLICIT: # EDF with implicit deadlines
        return SCHEDULABLE, "implicit deadlines and U <= 1 (Cor. 54)"

    if scheduler.fixed_task_priority and deadline_type != ARBITRARY: # RM/DM with constrained deadlines
        ordered = scheduler.sort_tasks(tasks)
        times = response_times(ordered)
        if None not in times:
            return SCHEDULABLE, f"response times {times} within the deadlines (Th. 29)"
        if taskset.is_synchronous():
            late = ordered[times.index(None)] # position of the first task that failed the response time test
            return NOT_SCHEDULABLE_ANALYSIS, f"tau{late.index + 1}: response time > D = {late.deadline} (Th. 29)"

    # what remains for simulation: arbitrary deadlines (FTP and EDF), EDF with constrained deadlines, and asynchronous
    # FTP sets that fail the synchronous test.
    start, end = feasibility_interval(tasks, scheduler)
    job = simulate(tasks, scheduler, start, end)
    if job is None:
        return SCHEDULABLE, f"no deadline miss in [{start}, {end})"
    return NOT_SCHEDULABLE_SIMULATION, (
        f"tau{job.task.index + 1} misses its deadline at {job.deadline} (job released at {job.release})"
    )
