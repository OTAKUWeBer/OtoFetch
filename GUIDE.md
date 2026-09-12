# 📚 OtoFetch Complete User Guide & Playbook

Welcome to the comprehensive guide for **OtoFetch**—the fast, lightweight, and accurate terminal music downloader for Spotify.

---

## 📑 Table of Contents

1. [Quick-Start Essentials](#1-quick-start-essentials)
2. [Audio Formats & Quality](#2-audio-formats--quality)
3. [Custom Directory & File Naming](#3-custom-directory--file-naming)
4. [Managing & Syncing Playlists](#4-managing--syncing-playlists)
5. [Lyrics & Playlist Files (.lrc & .m3u8)](#5-lyrics--playlist-files-lrc--m3u8)
6. [Speed & Performance Optimization](#6-speed--performance-optimization)
7. [Post-Download Summary & Auto-Reports](#7-post-download-summary--auto-reports)
8. [Advanced: Cookies & API Authentication](#8-advanced-cookies--api-authentication)
9. [Troubleshooting & FAQ](#9-troubleshooting--faq)

---

## 1. Quick-Start Essentials

OtoFetch automatically queries Spotify for metadata, finds matching high-quality audio streams across YouTube, YouTube Music, SoundCloud, and Bandcamp, and encodes full ID3 tags and album art into the file.

### 🎵 Single Song
```bash
otofetch "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"
```

### 💿 Complete Album
```bash
otofetch "https://open.spotify.com/album/4m28RiFDihEjKNJ4qpmXsA"
```

### 📑 Entire Playlist
```bash
otofetch "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
```

### 🔍 Direct Search (No link needed)
```bash
otofetch "Never Gonna Give You Up"
otofetch "artist:The Weeknd album:After Hours"
```

---

## 2. Audio Formats & Quality

By default, tracks are downloaded as **MP3** files in the highest available bitrate.

### 💎 Lossless FLAC
```bash
otofetch "TRACK_URL" --format flac
```

### 🎧 Other Formats
```bash
# AAC / M4A (Apple-compatible):
otofetch "TRACK_URL" --format m4a

# Opus (High compression efficiency):
otofetch "TRACK_URL" --format opus

# OGG Vorbis:
otofetch "TRACK_URL" --format ogg

# Uncompressed WAV:
otofetch "TRACK_URL" --format wav
```

### 🎚️ Custom Bitrate
```bash
otofetch "TRACK_URL" --bitrate 320k
```

---

## 3. Custom Directory & File Naming

By default, OtoFetch saves all downloaded music cleanly into your system's `Music/` folder:
`Music/{artists} - {title}.{output-ext}`

### 📂 Save into Subfolders (e.g. `Artist/Album/Song`)
```bash
otofetch "PLAYLIST_URL" --output "Music/{artist}/{album}/{title}.{output-ext}"
```

### 🏷️ Available Template Placeholders
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{title}` | Track title | `Blinding Lights` |
| `{artists}` | All contributing artists | `The Weeknd` |
| `{artist}` | Primary artist | `The Weeknd` |
| `{album}` | Album or EP name | `After Hours` |
| `{album-artist}` | Main album artist | `The Weeknd` |
| `{track-number}` | Track number on album | `09` |
| `{year}` | Release year | `2020` |
| `{output-ext}` | Output audio extension | `mp3` |

---

## 4. Managing & Syncing Playlists

Keep a local folder permanently synchronized with a Spotify playlist. OtoFetch automatically downloads newly added songs and cleans up tracks removed from the playlist:

### 1️⃣ Create a sync tracking file:
```bash
otofetch sync "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID" --save-file "my_playlist.otofetch"
```

### 2️⃣ Re-run synchronization whenever the playlist updates:
```bash
otofetch sync "my_playlist.otofetch"
```

---

## 5. Lyrics & Playlist Files (.lrc & .m3u8)

### 🎤 Synchronized Lyrics (.lrc)
Embed timed karaoke-style lyrics and create matching `.lrc` files for players like VLC, AIMP, and Apple Music:
```bash
otofetch "PLAYLIST_URL" --generate-lrc
```

### 📋 M3U8 Playlist Generation
Automatically generate an `.m3u8` playlist file to load all downloaded songs into your favorite media player:
```bash
otofetch "PLAYLIST_URL" --m3u "MyFavorites.m3u8"
```

---

## 6. Speed & Performance Optimization

For fast downloading of large playlists (200+ songs):

```bash
otofetch "PLAYLIST_URL" --threads 8
```

- **`--threads 8`**: Downloads 8 tracks simultaneously in parallel.

---

## 7. Post-Download Summary & Auto-Reports

Every download run concludes with a rich statistics overview:
- **Summary Metrics**: Total processed, successful downloads, duplicates/skipped, and failed count.
- **Speed & Duration**: Elapsed execution time and average processing throughput (songs/sec).
- **Unresolved Tracks Table**: Clear categorization of why any tracks were skipped or failed.
- **Auto-saved Report File (`logs/otofetch_report.txt`)**: A full timestamped log of all downloaded files, paths, and errors.
- **One-Click Retry File (`logs/otofetch_failed.txt`)**: Automatically generated when tracks fail. You can immediately retry all remaining songs:
  ```bash
  python -m otofetch "logs/otofetch_failed.txt"
  ```

---

## 8. Advanced: Cookies & API Authentication

### 🍪 Using YouTube Cookies (Premium Audio / Age-Restricted Tracks)
If you encounter age-gated tracks or want to use YouTube Premium audio streams:

```bash
otofetch "PLAYLIST_URL" --cookie-file "cookies.txt"
# OR direct browser cookie extraction:
otofetch "PLAYLIST_URL" --cookies-from-browser chrome
```
*(You can export `cookies.txt` using browser extensions like 'Get cookies.txt LOCALLY').*

### 🔑 Using Official Spotify Developer API
By default, OtoFetch uses anonymous access without needing keys. If you want to use your Spotify Developer account credentials:

```bash
otofetch "PLAYLIST_URL" --use-official-api --client-id "YOUR_ID" --client-secret "YOUR_SECRET"
```

---

## 9. Troubleshooting & FAQ

### Q: Why do I see `FFmpeg is not installed`?
**A:** Run `otofetch --download-ffmpeg` to let OtoFetch automatically download and set up a local FFmpeg binary.

### Q: What if a song is missing or gets interrupted halfway?
**A:** OtoFetch has built-in corruption detection. If a download was interrupted, it automatically detects zero-byte or incomplete files, cleans them up, and re-downloads fresh copies on the next run.

### Q: How do I update existing local audio files with missing album artwork?
**A:** Use the `meta` operation:
```bash
otofetch meta "Music/Artist - Title.mp3"
```
