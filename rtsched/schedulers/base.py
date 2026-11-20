"""Base classes for the schedulers.

A scheduler gives each job a priority key: a tuple where smaller means
higher priority. Keys are unique (they end with the task index and the job's
release), so the choice between ready jobs is always the same, whatever
their order in the list.

note:
    - I use tuples since Python compares tuples element by element.
      For RM, (T, index) means "the shortest period first; on a tie, the task that comes first in the file".
    - Why the keys are unique:
        - Two tasks never share an index.
        - Two jobs of the same task never share a release.
        - So min never has to choose between equal keys, and the result is deterministic, as the project rule requires.
"""

from rtsched.model import Job, Task


class Scheduler:
    """Common interface: `job_key` defines the priority, `pick` uses it."""

    name = ""
    fixed_task_priority = False

    def job_key(self, job: Job) -> tuple:
        """Priority key of a job; smaller = higher priority."""
        raise NotImplementedError

    def pick(self, ready_jobs: list[Job]) -> Job:
        """The ready job with the highest priority (the smallest key)."""
        return min(ready_jobs, key=self.job_key)


class FixedTaskPriority(Scheduler):
    """FTP scheduler (RM, DM): every job inherits the priority of its task.

    Jobs of the same task run oldest first (FIFO): the release is the last
    element of the key. With arbitrary deadlines a task can have several
    active jobs, and the older one must finish first.
    """

    fixed_task_priority = True

    def task_key(self, task: Task) -> tuple:
        """Priority key of a task; smaller = higher priority."""
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Tasks in decreasing priority order, as `s_n` and
        `response_times` expect (tau_1 = highest priority)."""
        return sorted(tasks, key=self.task_key)

    def job_key(self, job: Job) -> tuple:
        return self.task_key(job.task) + (job.release,) # task_key(...) + (job.release,): concatenates two tuples.
                                                        # For example, (10, 2) + (30,) is (10, 2, 30).
