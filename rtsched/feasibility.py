"""Feasibility intervals (curriculum guide chapters 3 and 4).

For a task set and a scheduler, the interval [start, end) the simulator must
cover: if no deadline is missed by the jobs released in it, none is ever
missed (Def. 31). Combinations without a known interval raise Unsupported.
"""

from rtsched.analysis import busy_period, hyperperiod, s_n
from rtsched.model import ARBITRARY, Task, TaskSet
from rtsched.schedulers import Scheduler


class Unsupported(Exception):
    """No feasibility interval is known for this combination (exit 2)."""


def check_supported(tasks: list[Task], scheduler: Scheduler) -> None:
    """Raise Unsupported when no feasibility interval is known: an FTP
    scheduler on an asynchronous set with arbitrary deadlines (Th. 44, 45
    and Cor. 46 need constrained deadlines)."""
    taskset = TaskSet(tasks)
    if (scheduler.fixed_task_priority and not taskset.is_synchronous()
            and taskset.deadline_type() == ARBITRARY):
        raise Unsupported(
            f"{scheduler.name.upper()} on an asynchronous task set with arbitrary deadlines: "
            "the curriculum guide gives no feasibility interval for fixed task priority "
            "schedulers in this case (Th. 44, 45 and Cor. 46 need constrained deadlines)"
        )

def feasibility_interval(tasks: list[Task], scheduler: Scheduler) -> tuple[int, int]:
    """The smallest known feasibility interval, as (start, end).

    - Synchronous, FTP, constrained deadlines: [0, min(D_max, lambda_n))
      (Cor. 32 and Th. 40, both are feasibility intervals).
    - Synchronous, FTP, arbitrary deadlines: [0, lambda_n) (Th. 40).
    - Synchronous, EDF: [0, L) (Cor. 59).
    - Asynchronous, FTP, constrained deadlines: [0, S_n + P) (Cor. 46).
    - Asynchronous, FTP, arbitrary deadlines: unsupported, the guide gives
      no interval (Th. 44, 45 and Cor. 46 need constrained deadlines).
    - Asynchronous, EDF: [0, O_max + 2P) (Cor. 63).

    A synchronous set whose offsets all equal O > 0 is the O = 0 schedule
    shifted by O, so its interval is shifted by O too.
    Requires U <= 1 (checked before, exit 3): lambda_n and L are only
    bounded then, and Cor. 63 assumes it.

    note:
        - busy_period gives both λ_n (FTP) and L (EDF). They're the same fixed point.
          Only the theorem that makes it a feasibility interval differs.
        - tasks[0].offset: in a synchronous set every offset is the same, so the first one is enough.
    """
    taskset = TaskSet(tasks)
    check_supported(tasks, scheduler)
    arbitrary = taskset.deadline_type() == ARBITRARY

    if taskset.is_synchronous():
        start = tasks[0].offset
        length = busy_period(tasks)
        if scheduler.fixed_task_priority and not arbitrary:
            length = min(length, max(task.deadline for task in tasks))
        return (start, start + length)

    if scheduler.fixed_task_priority:
        return (0, s_n(scheduler.sort_tasks(tasks)) + hyperperiod(tasks))

    o_max = max(task.offset for task in tasks)
    return (0, o_max + 2 * hyperperiod(tasks))
