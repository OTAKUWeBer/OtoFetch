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
7. [Advanced: Cookies & API Authentication](#7-advanced-cookies--api-authentication)
8. [Troubleshooting & FAQ](#8-troubleshooting--faq)

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

# Opus (High compression / streaming quality):
otofetch "TRACK_URL" --format opus

# OGG Vorbis:
otofetch "TRACK_URL" --format ogg

# Uncompressed WAV:
otofetch "TRACK_URL" --format wav
```

### 🎚️ Custom Bitrate
```bash
# Force 320 kbps MP3:
otofetch "TRACK_URL" --format mp3 --bitrate 320k

# Variable Bitrate (0 = highest VBR quality):
otofetch "TRACK_URL" --bitrate 0
```

---

## 3. Custom Directory & File Naming

By default, downloads are placed in the `Music/` folder. You can customize the folder structure using template variables.

### 📂 Organize by Playlist Name:
```bash
otofetch "PLAYLIST_URL" --output "Music/{list-name}/{artist} - {title}.{output-ext}"
```

### 📁 Organize by Artist & Album:
```bash
otofetch "PLAYLIST_URL" --output "Music/{album-artist}/{album}/{track-number} - {title}.{output-ext}"
```

### 🏷️ Available Template Variables:

| Variable | Description | Example |
|---|---|---|
| `{title}` | Track title | `Blinding Lights` |
| `{artist}` | Primary artist name | `The Weeknd` |
| `{artists}` | All contributing artists | `The Weeknd, Daft Punk` |
| `{album}` | Album name | `After Hours` |
| `{album-artist}` | Main album artist | `The Weeknd` |
| `{track-number}` | Track number on album | `01`, `02` |
| `{tracks-count}` | Total tracks on album | `14` |
| `{disc-number}` | Disc number | `1` |
| `{year}` | Release year | `2020` |
| `{genre}` | Primary genre | `Pop` |
| `{isrc}` | Track ISRC code | `USUM71900764` |
| `{list-name}` | Name of playlist or album | `My Top Hits` |
| `{output-ext}` | File extension | `mp3`, `flac` |

---

## 4. Managing & Syncing Playlists

The `sync` operation keeps a local music folder synchronized with a Spotify playlist:

```bash
# 1. Initial Sync & Save state:
otofetch sync "PLAYLIST_URL" --save-file my_playlist.otofetch

# 2. Later: Re-run to fetch new songs & remove deleted tracks:
otofetch sync "PLAYLIST_URL" --save-file my_playlist.otofetch
```

### Safe Syncing (Keep Local Songs):
If you want to download new songs without deleting songs that were removed from the Spotify playlist:
```bash
otofetch sync "PLAYLIST_URL" --save-file my_playlist.otofetch --sync-without-deleting
```

---

## 5. Lyrics & Playlist Files (.lrc & .m3u8)

### 🎤 Synchronized Lyrics (.lrc)
Generate timestamped `.lrc` files compatible with music players (VLC, Poweramp, Musicolet, foobar2000):
```bash
otofetch "PLAYLIST_URL" --generate-lrc
```

### 📋 M3U8 Playlist File
Generate a playlist file that your media player can load:
```bash
otofetch "PLAYLIST_URL" --m3u
```

---

## 6. Speed & Performance Optimization

For fast downloading of large playlists (200+ songs):

```bash
otofetch "PLAYLIST_URL" --threads 8 --lyrics
```

- **`--threads 8`**: Downloads 8 tracks simultaneously in parallel.
- **`--lyrics`** *(empty)*: Disables web scraping for lyric text, speeding up downloads.

---

## 7. Advanced: Cookies & API Authentication

### 🍪 Using YouTube Cookies (Premium Audio / Age-Restricted Tracks)
If you have YouTube Premium or want to bypass regional restrictions, pass a Netscape formatted cookies file:

```bash
otofetch "PLAYLIST_URL" --cookie-file "cookies.txt"
```
*(You can export `cookies.txt` from your browser using extensions like 'Get cookies.txt LOCALLY').*

### 🔑 Using Official Spotify Developer API
By default, OtoFetch uses anonymous access without needing keys. If you want to use your Spotify Developer account credentials:

```bash
otofetch "PLAYLIST_URL" --use-official-api --client-id "YOUR_ID" --client-secret "YOUR_SECRET"
```

---

## 8. Troubleshooting & FAQ

### Q: Why do I see `FFmpeg is not installed`?
**A:** Run `otofetch --download-ffmpeg` to let OtoFetch automatically download and set up a local FFmpeg binary.

### Q: What if a song is missing or gets interrupted halfway?
**A:** OtoFetch has built-in corruption detection. If a download was interrupted, it automatically detects zero-byte or incomplete files, cleans them up, and re-downloads fresh copies on the next run.

### Q: How do I update existing local audio files with missing album artwork?
**A:** Use the `meta` operation:
```bash
otofetch meta "Music/Artist - Title.mp3"
```
