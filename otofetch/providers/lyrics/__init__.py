"""
Lyrics providers for otofetch.
"""

from otofetch.providers.lyrics.azlyrics import AzLyrics
from otofetch.providers.lyrics.base import LyricsProvider
from otofetch.providers.lyrics.genius import Genius
from otofetch.providers.lyrics.musixmatch import MusixMatch
from otofetch.providers.lyrics.synced import Synced

__all__ = ["AzLyrics", "Genius", "MusixMatch", "Synced", "LyricsProvider"]
