"""Event-driven uniprocessor simulator.

Time jumps from one event to the next (a release, the completion of the
running job, or a deadline) instead of advancing one unit at a time.
Between two events the same job runs, so its remaining time drops by the
length of the gap.
"""

from rtsched.model import Job, Task
from rtsched.schedulers import Scheduler


def simulate(tasks: list[Task], scheduler: Scheduler, start: int, end: int) -> Job | None:
    """Simulate the jobs released in [start, end) and return the first job
    that misses its deadline, or None if every deadline is met.

    Jobs released before `end` are followed until they complete, so a
    deadline after `end` is still checked. The run stops at the first miss.
    A job finishing exactly at its deadline meets it.

    Ends: time strictly increases at each step (every event is later than
    now), only finitely many jobs are released before `end`, and each has
    finite work.
    """
    next_release = [task.offset for task in tasks]  # start <= every offset
    ready: list[Job] = []
    t = start

    while True:
        # 1. Deadline misses: an unfinished job whose deadline has passed.
        missed = [job for job in ready if job.deadline <= t]
        if missed:
            return min(missed, key=lambda job: (job.deadline, job.task.index)) # lambda creates a function that returns a tuple (job.deadline, job.task.index) for each job in missed.

        # 2. Releases at time t (only those inside the interval).
        for i, task in enumerate(tasks):
            if next_release[i] == t and t < end: # next_release[i] == t: the next release of task i is now, so we create a job for it.
                ready.append(Job(task, t, task.wcet))
                next_release[i] += task.period

        future = [r for r in next_release if r < end]

        # 3. Idle: jump to the next release, or stop if there is none.
        if not ready:
            if not future:
                return None
            t = min(future)
            continue

        # 4. Run the highest-priority job until the next event.
        job = scheduler.pick(ready)
        next_t = min([t + job.remaining] + future + [j.deadline for j in ready]) # next_t is the time of the next event: either the job finishes (t + job.remaining),
                                                                                 # or the next release (min(future)), or a deadline of a ready job (min(j.deadline for j in ready)).
        job.remaining -= next_t - t
        if job.remaining == 0:
            ready.remove(job)
        t = next_t
