"""
Module for holding console related actions.
"""

import json
import os
import sys

from contextlib import contextmanager
from rich.console import Console

from otofetch.utils.config import DEFAULT_CONFIG, get_config_file
from otofetch.utils.deno import download_deno as deno_download
from otofetch.utils.deno import get_local_deno, is_deno_installed
from otofetch.utils.ffmpeg import download_ffmpeg as ffmpeg_download
from otofetch.utils.ffmpeg import get_local_ffmpeg, is_ffmpeg_installed
from otofetch.utils.github import check_for_updates as get_update_status

__all__ = [
    "clear_terminal",
    "spinner_status",
    "StatusUpdater",
    "is_frozen",
    "is_executable",
    "generate_initial_config",
    "generate_config",
    "check_for_updates",
    "download_ffmpeg",
    "download_deno",
    "ACTIONS",
]

from rich import get_console


class StatusUpdater:
    """
    Helper wrapper for dynamic status message updates.
    """

    def __init__(self, status_obj=None) -> None:
        self._status = status_obj

    def update(self, text: str) -> None:
        """
        Update the active spinner text safely.
        """
        if self._status is not None:
            try:
                self._status.update(text)
            except Exception:
                pass


@contextmanager
def spinner_status(initial_message: str):
    """
    Context manager providing a single, rock-solid loading spinner with dynamic text updates.
    Uses get_console() directly without conflicting secondary displays.
    """
    console = get_console()
    try:
        with console.status(initial_message, spinner="dots") as status:
            yield StatusUpdater(status)
    except Exception:
        yield StatusUpdater(None)


def clear_terminal() -> None:
    """
    Clear the terminal/command prompt completely for maximum screen space.
    Works across Windows CMD, PowerShell, Windows Terminal, Linux, macOS, and ANSI shells.
    """
    try:
        if sys.stdout.isatty():
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")
            sys.stdout.write("\033[H\033[2J\033[3J")
            sys.stdout.flush()
    except Exception:
        pass


def is_frozen():
    """
    Check if the application is frozen.

    ### Returns
    - `True` if the application is frozen, `False` otherwise.
    """

    return getattr(sys, "frozen", False)


def is_executable():
    """
    Check if the application is an prebuilt executable.
    And has been launched with double click.

    ### Returns
    - `True` if the application is an prebuilt executable, `False` otherwise.
    """

    return is_frozen() and len(sys.argv) == 1


def generate_initial_config():
    """
    Generate the initial config file if it doesn't exist.
    """

    if get_config_file().is_file() is False:
        config_path = get_config_file()
        with open(config_path, "w", encoding="utf-8") as config_file:
            json.dump(DEFAULT_CONFIG, config_file, indent=4)


def generate_config():
    """
    Generate the config file if it doesn't exist
    This is done before the argument parser so it doesn't requires `operation`
    and `query` to be passed.
    """

    config_path = get_config_file()
    if config_path.exists():
        overwrite_config = input("Config file already exists. Overwrite? (y/N): ")

        if overwrite_config.lower() != "y":
            print("Exiting...")
            return None

    with open(config_path, "w", encoding="utf-8") as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)

    print(f"Config file generated at {config_path}")

    return None


def check_for_updates():
    """
    Check for updates to the current version.
    """

    version_message = get_update_status()

    print(version_message)


def download_ffmpeg():
    """
    Handle ffmpeg download process and print the result.
    """

    if get_local_ffmpeg() is not None or is_ffmpeg_installed():
        overwrite_ffmpeg = input(
            "FFmpeg is already installed. Do you want to overwrite it? (y/N): "
        )

        if overwrite_ffmpeg.lower() == "y":
            local_ffmpeg = ffmpeg_download()

            if local_ffmpeg.is_file():
                print(f"FFmpeg successfully downloaded to {local_ffmpeg.absolute()}")
            else:
                print("FFmpeg download failed")
    else:
        print("Downloading FFmpeg...")
        download_path = ffmpeg_download()

        if download_path.is_file():
            print(f"FFmpeg successfully downloaded to {download_path.absolute()}")
        else:
            print("FFmpeg download failed")


def download_deno():
    """
    Handle Deno download process and print the result.
    """

    if get_local_deno() is not None or is_deno_installed():
        download_deno_anyway = input(
            "Deno is already installed. Do you want to download it anyway? (y/N): "
        )

        if download_deno_anyway.lower() == "y":
            local_deno = deno_download()

            if local_deno.is_file():
                print(f"Deno successfully downloaded to {local_deno.absolute()}")
            else:
                print("Deno download failed")
    else:
        print("Downloading Deno...")
        download_path = deno_download()

        if download_path.is_file():
            print(f"Deno successfully downloaded to {download_path.absolute()}")
        else:
            print("Deno download failed")


ACTIONS = {
    "--generate-config": generate_config,
    "--check-for-updates": check_for_updates,
    "--download-ffmpeg": download_ffmpeg,
    "--download-deno": download_deno,
}
