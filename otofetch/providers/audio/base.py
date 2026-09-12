"""
Base audio provider module.
"""

import logging
import re
import shlex
from typing import Any, Dict, List, Optional, Tuple

from yt_dlp import YoutubeDL

from otofetch.types.result import Result
from otofetch.types.song import Song
from otofetch.utils.config import get_temp_path
from otofetch.utils.deno import get_local_deno_yt_dlp_options, warn_if_deno_missing
from otofetch.utils.formatter import (
    args_to_ytdlp_options,
    create_search_query,
    create_song_title,
)
from otofetch.utils.matching import get_best_matches, order_results

__all__ = ["AudioProviderError", "AudioProvider", "ISRC_REGEX", "YTDLLogger"]

logger = logging.getLogger(__name__)


class AudioProviderError(Exception):
    """
    Base class for all exceptions related to audio searching/downloading.
    """


class YTDLLogger:
    """
    Custom YT-dlp logger.
    """

    def debug(self, msg):
        """
        YTDL uses this to print debug messages.
        """

        pass  # pylint: disable=W0107

    def warning(self, msg):
        """
        YTDL uses this to print warnings.
        """

        pass  # pylint: disable=W0107

    def error(self, msg):
        """
        YTDL uses this to print errors.
        """

        # yt-dlp routes deprecation notices (e.g. old Python versions) through
        # the error channel; they are not download failures
        if "Deprecated Feature" in msg:
            logger.debug(msg)
            return

        raise AudioProviderError(msg)


ISRC_REGEX = re.compile(r"^[A-Z]{2}-?\w{3}-?\d{2}-?\d{5}$")


class AudioProvider:
    """
    Base class for all other providers. Provides some common functionality.
    Handles the yt-dlp audio handler.
    """

    SUPPORTS_ISRC: bool
    GET_RESULTS_OPTS: List[Dict[str, Any]]

    def __init__(
        self,
        output_format: str = "mp3",
        cookie_file: Optional[str] = None,
        search_query: Optional[str] = None,
        filter_results: bool = True,
        yt_dlp_args: Optional[str] = None,
    ) -> None:
        """
        Base class for audio providers.

        ### Arguments
        - output_directory: The directory to save the downloaded songs to.
        - output_format: The format to save the downloaded songs in.
        - cookie_file: The path to a file containing cookies to be used by YTDL.
        - search_query: The query to use when searching for songs.
        - filter_results: Whether to filter results.
        """

        self.output_format = output_format
        self.cookie_file = cookie_file
        self.search_query = search_query
        self.filter_results = filter_results

        if self.output_format == "m4a":
            ytdl_format = "bestaudio[ext=m4a]/bestaudio/best"
        elif self.output_format == "opus":
            ytdl_format = "bestaudio[ext=webm]/bestaudio/best"
        else:
            ytdl_format = "bestaudio/best"

        yt_dlp_options = {
            "format": ytdl_format,
            "quiet": True,
            "no_warnings": True,
            "encoding": "UTF-8",
            "logger": YTDLLogger(),
            "cookiefile": self.cookie_file,
            "outtmpl": str((get_temp_path() / "%(id)s.%(ext)s").resolve()),
            "retries": 5,
            "extractor_args": {},
        }

        yt_dlp_options.update(get_local_deno_yt_dlp_options())

        if yt_dlp_args:
            yt_dlp_options = args_to_ytdlp_options(
                shlex.split(yt_dlp_args), yt_dlp_options
            )

        self.audio_handler = YoutubeDL(yt_dlp_options)

    def get_results(self, search_term: str, **kwargs) -> List[Result]:
        """
        Get results from audio provider.

        ### Arguments
        - search_term: The search term to use.
        - kwargs: Additional arguments.

        ### Returns
        - A list of results.
        """

        raise NotImplementedError

    def get_views(self, url: str) -> int:
        """
        Get the number of views for a video.

        ### Arguments
        - url: The url of the video.

        ### Returns
        - The number of views.
        """

        data = self.get_download_metadata(url)

        return data["view_count"]

    def search_candidates(
        self, song: Song, only_verified: bool = False, limit: int = 4
    ) -> List[str]:
        """
        Search for a song and return top candidate download URLs in priority order.

        ### Arguments
        - song: The song to search for.
        - only_verified: Whether to accept only verified results.
        - limit: Maximum number of candidate URLs to return.

        ### Returns
        - List of candidate URLs in order of best match.
        """
        # Create initial search query
        search_query = create_song_title(song.name, song.artists).lower()
        if self.search_query:
            search_query = create_search_query(
                song, self.search_query, False, None, True
            )

        logger.debug("[%s] Searching for %s", song.song_id, search_query)

        candidates: List[str] = []
        isrc_urls: List[str] = []

        # search for song using isrc if it's available
        if song.isrc and self.SUPPORTS_ISRC and not self.search_query:
            isrc_results = self.get_results(song.isrc)

            if only_verified:
                isrc_results = [result for result in isrc_results if result.verified]
                logger.debug(
                    "[%s] Filtered to %s verified ISRC results",
                    song.song_id,
                    len(isrc_results),
                )

            isrc_urls = [result.url for result in isrc_results]
            logger.debug(
                "[%s] Found %s results for ISRC %s",
                song.song_id,
                len(isrc_results),
                song.isrc,
            )

            if len(isrc_results) == 1 and isrc_results[0].verified:
                candidates.append(isrc_results[0].url)

            elif len(isrc_results) > 0:
                sorted_isrc_results = order_results(
                    isrc_results, song, self.search_query
                )
                best_isrc_results = sorted(
                    sorted_isrc_results.items(), key=lambda x: x[1], reverse=True
                )
                for isrc_res, score in best_isrc_results:
                    if score >= 70.0 and isrc_res.url not in candidates:
                        candidates.append(isrc_res.url)

        # Build candidate search queries with smart regex cleanups for subtitles/brackets
        candidate_queries = [search_query]
        clean_name = re.sub(r"[\(\[].*?[\)\]]", "", song.name).strip()
        if clean_name and clean_name.lower() != song.name.lower():
            clean_query = create_song_title(clean_name, song.artists).lower()
            if clean_query not in candidate_queries:
                candidate_queries.append(clean_query)
            clean_artist_query = f"{song.artist} - {clean_name}".lower()
            if clean_artist_query not in candidate_queries:
                candidate_queries.append(clean_artist_query)

        # Query fallback using just title and first artist if multiple artists exist
        if len(song.artists) > 1:
            simple_artist_query = f"{song.artist} - {song.name}".lower()
            if simple_artist_query not in candidate_queries:
                candidate_queries.append(simple_artist_query)

        results: Dict[Result, float] = {}
        for query in candidate_queries:
            for options in self.GET_RESULTS_OPTS:
                try:
                    search_results = self.get_results(query, **options)
                except Exception as exc:
                    logger.debug("[%s] Provider search error for %s: %s", song.song_id, query, exc)
                    continue

                if only_verified:
                    search_results = [
                        result for result in search_results if result.verified
                    ]

                logger.debug(
                    "[%s] Found %s results for search query %s with options %s",
                    song.song_id,
                    len(search_results),
                    query,
                    options,
                )

                # Priority match from ISRC
                isrc_result = next(
                    (result for result in search_results if result.url in isrc_urls),
                    None,
                )
                if isrc_result and isrc_result.url not in candidates:
                    candidates.append(isrc_result.url)

                if self.filter_results:
                    new_results = order_results(search_results, song, self.search_query)
                else:
                    new_results = {r: 100.0 for r in search_results}

                results.update(new_results)

        # Sort all aggregated results by composite score
        if results:
            best_matches = get_best_matches(results, limit=limit * 2)
            for res, score in best_matches:
                if score >= 50.0 and res.url not in candidates:
                    candidates.append(res.url)

        return candidates[:limit]

    def search(self, song: Song, only_verified: bool = False) -> Optional[str]:
        """
        Search for a song and return best match URL.
        """
        candidates = self.search_candidates(song, only_verified=only_verified, limit=1)
        return candidates[0] if candidates else None

    def get_best_result(self, results: Dict[Result, float]) -> Tuple[Result, float]:
        """
        Get the best match from the results
        using views and average match

        ### Arguments
        - results: A dictionary of results and their scores

        ### Returns
        - The best match URL and its score
        """

        best_results = get_best_matches(results, 8)

        # If we have only one result, return it
        if len(best_results) == 1:
            return best_results[0][0], best_results[0][1]

        # Initial best result based on the average match
        best_result = best_results[0]

        # If the best result has a score higher than 80%
        # and it's a isrc search, return it
        if best_result[1] > 80 and best_result[0].isrc_search:
            return best_result[0], best_result[1]

        # If we have more than one result,
        # return the one with the highest score
        # and most views
        if len(best_results) > 1:
            views: List[int] = []
            for best_result in best_results:
                if best_result[0].views:
                    views.append(best_result[0].views)
                else:
                    views.append(self.get_views(best_result[0].url))

            highest_views = max(views)
            lowest_views = min(views)

            if highest_views in (0, lowest_views):
                return best_result[0], best_result[1]

            weighted_results: List[Tuple[Result, float]] = []
            for index, best_result in enumerate(best_results):
                result_views = views[index]
                views_score = (
                    (result_views - lowest_views) / (highest_views - lowest_views)
                ) * 15
                score = min(best_result[1] + views_score, 100)
                weighted_results.append((best_result[0], score))

            # Now we return the result with the highest score
            return max(weighted_results, key=lambda x: x[1])

        return best_result[0], best_result[1]

    def get_download_metadata(self, url: str, download: bool = False) -> Dict:
        """
        Get metadata for a download using yt-dlp.

        ### Arguments
        - url: The url to get metadata for.

        ### Returns
        - A dictionary containing the metadata.
        """

        try:
            data = self.audio_handler.extract_info(url, download=download)

            if data:
                return data
        except Exception as exception:
            if download:
                warn_if_deno_missing()

            logger.debug(exception)
            raise AudioProviderError(f"YT-DLP download error - {url}") from exception

        raise AudioProviderError(f"No metadata found for the provided url {url}")

    @property
    def name(self) -> str:
        """
        Get the name of the provider.

        ### Returns
        - The name of the provider.
        """

        return self.__class__.__name__
