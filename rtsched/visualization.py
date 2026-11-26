"""Gantt chart of a simulated schedule (bonus, matplotlib).

One row per task: a bar for every stretch of execution, a triangle at every
job release, and a red cross at the first missed deadline. The chart is only
for display: it runs its own simulation and never changes a verdict.
"""

import matplotlib

matplotlib.use("Agg")  # draw into a file, no window
import matplotlib.pyplot as plt

from rtsched.feasibility import feasibility_interval
from rtsched.model import Task
from rtsched.schedulers import Scheduler
from rtsched.simulator import simulate

MAX_LENGTH = 200  # longest window drawn, in time units


def drawing_window(tasks: list[Task], scheduler: Scheduler) -> tuple[int, int, int]:
    """(start, end, full_end): the feasibility interval [start, full_end),
    cut to at most MAX_LENGTH time units. When U > 1 there is no interval
    (no busy period), so the window is [0, MAX_LENGTH)."""
    try:
        start, full_end = feasibility_interval(tasks, scheduler)
    except ValueError:
        start, full_end = 0, MAX_LENGTH
    return start, min(full_end, start + MAX_LENGTH), full_end


def plot_core(tasks: list[Task], scheduler: Scheduler, path: str, title: str) -> None:
    """Simulate the drawing window and save the Gantt chart to `path` (PNG)."""
    start, end, full_end = drawing_window(tasks, scheduler)
    trace: list = []
    missed = simulate(tasks, scheduler, start, end, trace)

    # Jobs released before `end` may run after it; a miss stops the run early.
    right = max([end] + [stop for *_, stop in trace])
    if missed is not None:
        right = max([missed.deadline] + [stop for *_, stop in trace])
    row = {task.index: k for k, task in enumerate(tasks)}  # tau1 of the core on top

    fig, ax = plt.subplots(figsize=(10, 0.6 * len(tasks) + 1.5))
    for index, _release, begin, stop in trace:
        ax.broken_barh([(begin, stop - begin)], (row[index] - 0.35, 0.7), color=f"C{index % 10}",
                       edgecolor="black", linewidth=0.5)
    for task in tasks:
        k = 0
        while task.release_time(k) < min(end, right):
            ax.plot(task.release_time(k), row[task.index] - 0.45, "^", color="black", markersize=5)
            k += 1
    if missed is not None:
        ax.plot(missed.deadline, row[missed.task.index], "x", color="red", markersize=14, markeredgewidth=3)

    ax.set_yticks(range(len(tasks)), [f"tau{task.index + 1}" for task in tasks])
    ax.set_ylim(len(tasks) - 0.4, -0.7)
    margin = (right - start) * 0.02  # keep the markers at both ends visible
    ax.set_xlim(start - margin, right + margin)
    ax.set_xlabel("time")
    ax.grid(axis="x", alpha=0.3)
    window = f"[{start}, {end})" if end == full_end else f"first {end - start} units of [{start}, {full_end})"
    status = "no deadline miss" if missed is None else f"tau{missed.task.index + 1} misses at {missed.deadline}"
    ax.set_title(f"{title}, {scheduler.name.upper()}, {window}: {status}")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
