"""Earliest Deadline First (curriculum guide Def. 12, chapter 4)."""

from rtsched.model import Job
from rtsched.schedulers.base import Scheduler


class EDF(Scheduler):
    """Earliest Deadline First: the job with the earliest absolute deadline
    has the highest priority (Def. 12).

    Ties (equal absolute deadlines) go to the task that comes first in the
    file. EDF is optimal on a uniprocessor (Th. 52).

    note: Why EDF is a fixed job priority (FJP) scheduler: a job's absolute deadline
    is fixed once it's released, so its priority never changes.
    Two jobs of the same task get different priorities, though, which is why
    there's no task_key or sort_tasks, and why fixed_task_priority stays False (from Scheduler).
    """

    name = "edf"

    def job_key(self, job: Job) -> tuple:
        return (job.deadline, job.task.index, job.release)
