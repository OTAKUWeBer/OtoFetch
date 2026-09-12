"""
Main module for otofetch. Exports version and main function.
"""

from otofetch._version import __version__
from otofetch.console import console_entry_point

if __name__ == "__main__":
    console_entry_point()
