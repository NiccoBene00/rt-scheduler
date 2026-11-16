"""Exit codes of the program (section 4.2 of the project description)."""

SCHEDULABLE = 0                 # the system is schedulable
PARTITION_FAILED = 1            # a task fits on no core (U > 1 on every core)
UNSUPPORTED = 2                 # no known feasibility interval for this task model / algorithm
NOT_SCHEDULABLE_ANALYSIS = 3    # not schedulable, decided without simulation
NOT_SCHEDULABLE_SIMULATION = 4  # not schedulable, a deadline miss was found by simulation
INVALID_INPUT = 5               # my addition: bad arguments or a malformed task file
