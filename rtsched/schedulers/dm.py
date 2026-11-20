"""Deadline Monotonic (curriculum guide Section 3.4)."""

from rtsched.model import Task
from rtsched.schedulers.base import FixedTaskPriority


class DM(FixedTaskPriority):
    """Deadline Monotonic: the shorter the relative deadline, the higher
    the priority.

    Ties (equal deadlines) go to the task that comes first in the file.
    DM is FTP-optimal for synchronous constrained-deadline systems (Th. 35).
    With implicit deadlines (D = T) it gives the same order as RM.
    """

    name = "dm"

    # The only difference from RM is task.deadline instead of task.period in the key.
    def task_key(self, task: Task) -> tuple:
        return (task.deadline, task.index)
