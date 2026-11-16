"""Task model: periodic tasks, the jobs they release, and task sets.

I here use the notation of the course: task tau_i = (O_i, C_i, D_i, T_i), with offset O_i,
worst-case execution time C_i, relative deadline D_i and period T_i.

Note:
    - I use Fraction for utilization, to avoid rounding errors.
    - I use frozen=True makes a task impossible to change after it's created, since a task's parameters are fixed.
      Job isn't frozen, because its remaining execution time changes while the job runs.
"""

from dataclasses import dataclass
from fractions import Fraction

# Deadline types (curriculum guide, chapter 2)
IMPLICIT = "implicit"        # D_i = T_i for every task
CONSTRAINED = "constrained"  # D_i <= T_i for every task
ARBITRARY = "arbitrary"      # no relation between D_i and T_i


@dataclass(frozen=True)
class Task:
    """A periodic task. `index` is its line number in the file (0-based),
    used to break priority ties the same way every time."""

    index: int
    offset: int
    wcet: int
    deadline: int
    period: int

    def utilization(self) -> Fraction:
        """U_i = C_i / T_i, as an exact fraction."""
        return Fraction(self.wcet, self.period)

    def release_time(self, k: int) -> int:
        """Release time of the k-th job (k = 0, 1, 2, ...): O_i + k * T_i."""
        return self.offset + k * self.period


@dataclass
class Job:
    """One job of a task: released at `release`, must receive `task.wcet`
    units of CPU before its absolute deadline `release + task.deadline`."""

    task: Task
    release: int
    remaining: int

    @property
    def deadline(self) -> int:
        """Absolute deadline d = release + D_i."""
        return self.release + self.task.deadline


class TaskSet:
    """A list of tasks, plus the properties that decide which theory applies.

    note: Under is_synchronous, offsets that are all equal but not 0 (for example every task at O = 5)
    still count as synchronous. The schedule is then the O = 0 schedule shifted by 5, so the same intervals apply, moved by 5.
    I'll take care of that shift in feasibility.py."""

    def __init__(self, tasks: list[Task]):
        self.tasks = tasks

    def utilization(self) -> Fraction:
        """U(tau) = sum of C_i / T_i."""
        return sum((task.utilization() for task in self.tasks), Fraction(0))

    def is_synchronous(self) -> bool:
        """Synchronous: every task releases its first job at the same instant.
        note: the set {offeset} reports the number of distinct offsets, so if it's <= 1, all tasks have the same offset."""
        return len({task.offset for task in self.tasks}) <= 1

    def deadline_type(self) -> str:
        """IMPLICIT, CONSTRAINED or ARBITRARY (the most specific one that holds)."""
        if all(task.deadline == task.period for task in self.tasks):
            return IMPLICIT
        if all(task.deadline <= task.period for task in self.tasks):
            return CONSTRAINED
        return ARBITRARY

    def describe(self) -> str:
        """Short description for messages, e.g. 'asynchronous constrained'."""
        timing = "synchronous" if self.is_synchronous() else "asynchronous"
        return f"{timing} {self.deadline_type()}"
