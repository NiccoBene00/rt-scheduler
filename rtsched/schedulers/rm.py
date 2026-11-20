"""Rate Monotonic (curriculum guide Section 3.3)."""

from rtsched.model import Task
from rtsched.schedulers.base import FixedTaskPriority


class RM(FixedTaskPriority):
    """Rate Monotonic: the shorter the period, the higher the priority.

    Ties (equal periods) go to the task that comes first in the file.
    RM is FTP-optimal for synchronous implicit-deadline systems (Th. 28).
    """

    name = "rm"

    # job_key, pick and sort_tasks are inherited from FixedTaskPriority.
    # RM only says what ranks a task: the period, then the line in the file.
    def task_key(self, task: Task) -> tuple:
        return (task.period, task.index)
