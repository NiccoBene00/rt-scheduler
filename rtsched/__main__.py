"""Entry point for `python -m rtsched <task_file> -a rm ...`."""

import sys

from rtsched.cli import main

if __name__ == "__main__":
    sys.exit(main())
