"""
Module for getting information about the current version of otofetch
from GitHub and checking for updates.
"""

import logging
from typing import Tuple

import requests

from otofetch import _version

__all__ = [
    "REPO",
    "get_status",
    "check_for_updates",
    "get_latest_version",
]

REPO = "OTAKUWeBer/OtoFetch"


class RateLimitError(Exception):
    """
    Raised when the GitHub API rate limit is exceeded.
    """


def get_status(start: str, end: str, repo: str = REPO) -> Tuple[str, int, int]:
    """
    Get the status of a commit range.

    ### Arguments
    - start: the starting commit/branch/tag
    - end: the ending commit/branch/tag
    - repo: the repo to check (defaults to OTAKUWeBer/OtoFetch)

    ### Returns
    - tuple of (status, ahead_by, behind_by)
    """

    url = f"https://api.github.com/repos/{repo}/compare/{start}...{end}"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        if response.status_code == 403:
            raise RateLimitError("GitHub API rate limit exceeded.")

        raise RuntimeError(
            f"Failed to get commit count. Status code: {response.status_code}"
        )

    data = response.json()

    return (
        data["status"],
        data["ahead_by"],
        data["behind_by"],
    )


def get_latest_version(repo: str = REPO) -> str:
    """
    Get the latest version of the repo.

    ### Arguments
    - repo: the repo to check (defaults to OTAKUWeBer/OtoFetch)

    ### Returns
    - the latest version
    """

    response = requests.get(
        f"https://api.github.com/repos/{repo}/releases/latest",
        timeout=10,
    )

    if response.status_code != 200:
        if response.status_code == 403:
            raise RateLimitError("GitHub API rate limit exceeded.")

        raise RuntimeError(
            f"Failed to get latest version. Status code: {response.status_code}"
        )

    json_data = response.json()

    return json_data["tag_name"]


def check_for_updates(repo: str = REPO) -> str:
    """
    Check for updates to the repo.

    ### Arguments
    - repo: the repo to check (defaults to OTAKUWeBer/OtoFetch)

    ### Returns
    - a message indicating whether or not there are updates
    """

    version = _version.__version__

    try:
        latest_version = get_latest_version(repo)
    except RateLimitError:
        return "GitHub API rate limit exceeded while checking for updates."
    except Exception as e:
        return f"Failed to check for updates: {e}"

    if version != latest_version:
        return f"A new version of OtoFetch is available: {latest_version} (current: {version})"

    return "OtoFetch is up to date."
