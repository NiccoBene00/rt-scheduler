"""Partitioning of a task set among identical cores (Section 3.5 of the project description,
curriculum guide Section 7.1.1).

Bin packing: each core has capacity 1, and a task fits on a core when the
core's utilization plus U_i stays <= 1 (exact Fraction). The tasks are first
sorted by utilization, then placed one by one with a greedy heuristic.
"""

from fractions import Fraction

from rtsched.model import Task


def sort_by_utilization(tasks: list[Task], order: str) -> list[Task]:
    """'du' = decreasing utilization, 'iu' = increasing; ties by index."""
    if order == "du":
        return sorted(tasks, key=lambda task: (-task.utilization(), task.index)) # firts sort by utilization in decreasing order, then by index in increasing order if a tie occurs
    return sorted(tasks, key=lambda task: (task.utilization(), task.index)) # first sort by utilization in increasing order, then by index in increasing order if a tie occurs


def partition(tasks: list[Task], cores: int, heuristic: str, order: str) -> list[list[Task]] | None:
    """The tasks of each core (in file order), or None if a task fits on
    no core (partitioning fails, exit 1).

    - ff (first fit): the first core where the task fits.
    - bf (best fit): the core with the highest load where it fits.
    - wf (worst fit): the core with the lowest load where it fits.
    - nf (next fit): the current core if it fits, otherwise the next ones;
      it never goes back to an earlier core.
    Ties between cores go to the lowest core number.
    """
    load = [Fraction(0)] * cores # list of 'cores' elementts, filled with fraction 0, representing the current load of each core
    assigned: list[list[Task]] = [[] for _ in range(cores)] # list of 'cores' empty lists, representing the tasks assigned to each core
    current = 0  # next fit: the core being filled

    for task in sort_by_utilization(tasks, order):
        u = task.utilization()
        if heuristic == "nf":
            while current < cores and load[current] + u > 1:
                current += 1
            if current == cores:
                return None
            core = current
        else: # branch for ff, bf, wf
            eligible = [k for k in range(cores) if load[k] + u <= 1] # cores for which the task fits (load + utilization <= 1)
            if not eligible: # if no eligible cores, return None
                return None
            if heuristic == "ff":
                core = eligible[0]
            elif heuristic == "bf":
                core = min(eligible, key=lambda k: (-load[k], k)) # with the minus sign, we are looking for the core with the highest load (best fit), and in case of a tie, the lowest core number
            else:  # wf
                core = min(eligible, key=lambda k: (load[k], k))
        load[core] += u # update the load of the core with the utilization of the task
        assigned[core].append(task) # add the task to the list of tasks assigned to that core

    return [sorted(core_tasks, key=lambda task: task.index) for core_tasks in assigned] # return the list of tasks assigned to each core, sorted by their original index
