"""Schedulers: RM, DM (fixed task priority) and EDF (fixed job priority).

`get_scheduler` turns the name given with -a into a scheduler object.

note:
    - this file makes schedulers/ a package and is run on import rtsched.schedulers.
      The imports let other modules write from rtsched.schedulers import RM,
      get_scheduler instead of going through the individual files.
    -
"""

from rtsched.schedulers.base import FixedTaskPriority, Scheduler
from rtsched.schedulers.dm import DM
from rtsched.schedulers.edf import EDF
from rtsched.schedulers.rm import RM

SCHEDULERS = {cls.name: cls for cls in (RM, DM, EDF)}


def get_scheduler(name: str) -> Scheduler:
    """A new scheduler object for 'rm', 'dm' or 'edf'."""
    return SCHEDULERS[name]() # looks up the class and calls it to create an object. An unknown name would raise KeyError,
                              # but argparse already rejects it with exit 5 before this function is reached.

