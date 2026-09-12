"""
Module that holds the entry point for the console.
"""

import cProfile
import logging
import pstats
import signal
import sys
import time

from otofetch.console.download import download
from otofetch.console.meta import meta
from otofetch.console.save import save
from otofetch.console.sync import sync
from otofetch.console.url import url
from otofetch.download.downloader import Downloader, DownloaderError
from otofetch.utils.arguments import parse_arguments
from otofetch.utils.config import create_settings
from otofetch.utils.console import ACTIONS, generate_initial_config, is_executable
from otofetch.utils.downloader import check_ytmusic_connection
from otofetch.utils.ffmpeg import FFmpegError, download_ffmpeg, is_ffmpeg_installed
from otofetch.utils.logging import init_logging
from otofetch.utils.spotify import SpotifyClient, SpotifyError, save_spotify_cache

__all__ = ["console_entry_point", "OPERATIONS"]

OPERATIONS = {
    "download": download,
    "sync": sync,
    "save": save,
    "meta": meta,
    "url": url,
}

logger = logging.getLogger(__name__)


def console_entry_point():
    """
    Entry point for the console. With profile flag, it runs the code with cProfile.
    """

    if "--profile" in sys.argv:
        with cProfile.Profile() as profile:
            entry_point()

        stats = pstats.Stats(profile)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats("otofetch.profile")
    else:
        entry_point()


def entry_point():
    """
    Console entry point for otofetch. This is where the magic happens.
    """

    # Create config file if it doesn't exist
    generate_initial_config()

    # Check if sys.argv contains an action
    # If it does, we run the action and exit
    try:
        action_to_run = next(
            action for action_name, action in ACTIONS.items() if action_name in sys.argv
        )
    except StopIteration:
        action_to_run = None

    if action_to_run:
        action_to_run()
        return None

    # Parse the arguments
    arguments = parse_arguments()

    # Create settings dicts
    spotify_settings, downloader_settings = create_settings(arguments)

    init_logging(downloader_settings["log_level"], downloader_settings["log_format"])

    # If the application is frozen, we check for ffmpeg
    # if it's not present download it create config file
    if is_executable():
        if is_ffmpeg_installed() is False:
            download_ffmpeg()

    # Check if ffmpeg is installed
    if is_ffmpeg_installed(downloader_settings["ffmpeg"]) is False:
        raise FFmpegError(
            "FFmpeg is not installed. Please run `otofetch --download-ffmpeg` to install it, "
            "or `otofetch --ffmpeg /path/to/ffmpeg` to specify the path to ffmpeg."
        )

    # Check if we might be blocked by YouTube Music without stopping downloads.
    if "youtube-music" in downloader_settings["audio_providers"]:
        if not check_ytmusic_connection():
            logger.warning(
                "You might be blocked by YouTube Music. "
                "If downloads fail, use a VPN, or use other audio providers. "
            )

    # Initialize spotify client
    SpotifyClient.init(**spotify_settings)
    spotify_client = SpotifyClient()

    # Check if save file is present and if it's valid
    if isinstance(downloader_settings["save_file"], str) and (
        not downloader_settings["save_file"].endswith(".otofetch")
        and not downloader_settings["save_file"] == "-"
    ):
        raise DownloaderError("Save file has to end with .otofetch")

    # Check if the user is logged in
    if (
        arguments.query
        and "saved" in arguments.query
        and not spotify_settings["user_auth"]
    ):
        raise SpotifyError(
            "You must be logged in to use the saved query. "
            "Log in by adding the --user-auth flag"
        )

    # Initialize the downloader
    # for download, load and preload operations
    downloader = Downloader(downloader_settings)

    def graceful_exit(_signal, _frame):
        if spotify_settings["use_cache_file"]:
            save_spotify_cache(spotify_client.cache)

        downloader.progress_handler.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    start_time = time.perf_counter()

    try:
        # Pick the operation to perform
        # based on the name and run it!
        OPERATIONS[arguments.operation](
            query=arguments.query,
            downloader=downloader,
        )
    except Exception as exc:
        if downloader_settings["save_errors"]:
            with open(
                downloader_settings["save_errors"], "a", encoding="utf-8"
            ) as error_file:
                error_file.write("\n".join([exc + "\n" for exc in exc.args]))

            logger.debug("Saved errors to %s", downloader_settings["save_errors"])

        end_time = time.perf_counter()
        logger.debug("Took %d seconds", end_time - start_time)

        downloader.progress_handler.close()
        logger.exception("An error occurred")

        sys.exit(1)

    end_time = time.perf_counter()
    logger.debug("Took %d seconds", end_time - start_time)

    if spotify_settings["use_cache_file"]:
        save_spotify_cache(spotify_client.cache)

    downloader.progress_handler.close()

    return None
