"""
Main module for otofetch. Exports version and main function.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from otofetch._version import __version__
from otofetch.console import console_entry_point

if __name__ == "__main__":
    console_entry_point()
