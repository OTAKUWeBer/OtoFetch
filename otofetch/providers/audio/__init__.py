"""
Audio providers for otofetch.
"""

from otofetch.providers.audio.bandcamp import BandCamp
from otofetch.providers.audio.base import (
    ISRC_REGEX,
    AudioProvider,
    AudioProviderError,
    YTDLLogger,
)
from otofetch.providers.audio.piped import Piped
from otofetch.providers.audio.soundcloud import SoundCloud
from otofetch.providers.audio.youtube import YouTube
from otofetch.providers.audio.ytmusic import YouTubeMusic

__all__ = [
    "YouTube",
    "YouTubeMusic",
    "SoundCloud",
    "BandCamp",
    "Piped",
    "AudioProvider",
    "AudioProviderError",
    "YTDLLogger",
    "ISRC_REGEX",
]
