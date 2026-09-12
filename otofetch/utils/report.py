"""
Reporting and summary module for OtoFetch.
Provides rich terminal summary tables and automated text report generation.
"""

import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from otofetch.types.song import Song


def format_duration(seconds: float) -> str:
    """Format duration in seconds to a human readable mm:ss or hh:mm:ss string."""
    seconds_int = int(seconds)
    if seconds_int < 60:
        return f"{seconds_int}s"
    minutes = seconds_int // 60
    rem_seconds = seconds_int % 60
    if minutes < 60:
        return f"{minutes}m {rem_seconds:02d}s"
    hours = minutes // 60
    rem_minutes = minutes % 60
    return f"{hours}h {rem_minutes:02d}m {rem_seconds:02d}s"


def clean_reason(error_msg: str) -> str:
    """Clean and categorize an error message for concise presentation."""
    msg = str(error_msg)
    if "Sign in to confirm your age" in msg or "confirm your age" in msg:
        return "Age restricted (Requires --cookies-from-browser)"
    if "This video is not available" in msg or "Video unavailable" in msg:
        return "YouTube video unavailable / geo-blocked"
    if "No results found for song" in msg or "LookupError" in msg:
        return "No usable match found across audio providers"
    if "ffmpeg" in msg.lower() or "convert" in msg.lower():
        return "Audio conversion / FFmpeg error"
    if "metadata" in msg.lower():
        return "Metadata embedding error"
    if "HTTP Error 429" in msg or "Too Many Requests" in msg:
        return "Rate limited (Too Many Requests)"

    # Shorten generic errors
    if len(msg) > 65:
        msg = msg[:62] + "..."
    return msg


def print_download_summary(
    total_requested: int,
    downloaded_songs: List[Tuple[Song, Path]],
    skipped_songs: List[Tuple[Song, Path]],
    failed_songs: List[Tuple[Song, str]],
    duration: float,
    output_dir: str = "Music",
    logs_dir: str = "logs",
) -> Tuple[Path, Optional[Path]]:
    """
    Print a professional Rich summary table to the console and save report files in logs/.

    ### Returns
    - Tuple of (report_file_path, failed_file_path_or_none)
    """
    console = Console()

    downloaded_count = len(downloaded_songs)
    skipped_count = len(skipped_songs)
    failed_count = len(failed_songs)
    total_processed = downloaded_count + skipped_count + failed_count
    if total_requested > total_processed:
        total_processed = total_requested

    speed = f"{(total_processed / duration):.1f} songs/s" if duration > 0 else "N/A"
    duration_str = format_duration(duration)

    # 1. Summary Metrics Panel
    metrics_text = Text()
    metrics_text.append("  Total Processed    : ", style="bold")
    metrics_text.append(f"{total_processed}\n", style="bold white")

    metrics_text.append("  [OK] Downloaded    : ", style="bold green")
    metrics_text.append(f"{downloaded_count}\n", style="bold green")

    metrics_text.append("  [--] Skipped       : ", style="bold yellow")
    metrics_text.append(f"{skipped_count} (already existing in library)\n", style="yellow")

    metrics_text.append("  [XX] Failed        : ", style="bold red" if failed_count > 0 else "bold green")
    metrics_text.append(f"{failed_count}\n", style="bold red" if failed_count > 0 else "bold green")

    metrics_text.append("  Time Elapsed       : ", style="bold")
    metrics_text.append(f"{duration_str}\n", style="cyan")

    metrics_text.append("  Average Speed      : ", style="bold")
    metrics_text.append(f"{speed}\n", style="cyan")

    metrics_text.append("  Output Directory   : ", style="bold")
    metrics_text.append(f"{output_dir}\n", style="magenta")

    panel = Panel(
        metrics_text,
        title="[bold cyan] OtoFetch Download Summary [/bold cyan]",
        subtitle="[cyan]Fast, Accurate Spotify Downloader[/cyan]",
        border_style="cyan",
        padding=(0, 2),
    )
    console.print()
    console.print(panel)

    # 2. Failed Tracks Table (if any)
    if failed_songs:
        failed_table = Table(
            title="[bold red]Unresolved Tracks[/bold red]",
            show_header=True,
            header_style="bold red",
            border_style="dim red",
        )
        failed_table.add_column("#", style="dim", width=4, justify="right")
        failed_table.add_column("Track", style="bold white", min_width=30, max_width=45, overflow="ellipsis")
        failed_table.add_column("Reason", style="yellow", min_width=35)

        # Show up to 12 in the terminal table so it doesn't flood the viewport
        limit = 12
        for idx, (song, reason) in enumerate(failed_songs[:limit], start=1):
            clean_r = clean_reason(reason)
            failed_table.add_row(str(idx), song.display_name, clean_r)

        console.print(failed_table)
        if len(failed_songs) > limit:
            console.print(
                f"[dim yellow]... and {len(failed_songs) - limit} more failed tracks listed in the report file below.[/dim yellow]"
            )

    # 3. Save Text Report and Retry File into dedicated logs/ directory
    report_file, retry_file = save_reports(
        total_requested=total_processed,
        downloaded_songs=downloaded_songs,
        skipped_songs=skipped_songs,
        failed_songs=failed_songs,
        duration=duration,
        output_dir=output_dir,
        logs_dir=logs_dir,
    )

    console.print(f"[bold cyan]Report Saved[/bold cyan] : [white]{report_file.resolve()}[/white]")
    if retry_file:
        console.print(f"[bold yellow]Retry List  [/bold yellow] : [white]{retry_file.resolve()}[/white]")
        console.print(
            f"[dim]To retry failed songs, run: [bold green]python -m otofetch \"{retry_file}\"[/bold green][/dim]"
        )
    console.print()

    return report_file, retry_file


def save_reports(
    total_requested: int,
    downloaded_songs: List[Tuple[Song, Path]],
    skipped_songs: List[Tuple[Song, Path]],
    failed_songs: List[Tuple[Song, str]],
    duration: float,
    output_dir: str = "Music",
    logs_dir: str = "logs",
) -> Tuple[Path, Optional[Path]]:
    """Save full report and failed-songs list to text files in a dedicated logs/ folder."""
    log_path = Path(logs_dir) if logs_dir else Path("logs")
    try:
        log_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        log_path = Path(".")

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duration_str = format_duration(duration)

    report_file = log_path / "otofetch_report.txt"
    retry_file: Optional[Path] = None

    # Write otofetch_report.txt
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  OTOFETCH DOWNLOAD REPORT - {now_str}\n")
        f.write("=" * 70 + "\n\n")

        f.write("SUMMARY STATISTICS:\n")
        f.write(f"  Total Requested : {total_requested}\n")
        f.write(f"  Downloaded      : {len(downloaded_songs)}\n")
        f.write(f"  Skipped         : {len(skipped_songs)} (Already exist)\n")
        f.write(f"  Failed          : {len(failed_songs)}\n")
        f.write(f"  Duration        : {duration_str}\n")
        f.write(f"  Music Folder    : {Path(output_dir).resolve() if output_dir else Path('.').resolve()}\n\n")

        if failed_songs:
            f.write("-" * 70 + "\n")
            f.write(f"FAILED TRACKS ({len(failed_songs)}):\n")
            f.write("-" * 70 + "\n")
            for idx, (song, reason) in enumerate(failed_songs, start=1):
                f.write(f"{idx:3d}. {song.display_name}\n")
                f.write(f"     Spotify URL: {song.url}\n")
                f.write(f"     Reason     : {reason}\n\n")

        if downloaded_songs:
            f.write("-" * 70 + "\n")
            f.write(f"SUCCESSFULLY DOWNLOADED ({len(downloaded_songs)}):\n")
            f.write("-" * 70 + "\n")
            for idx, (song, path) in enumerate(downloaded_songs, start=1):
                f.write(f"{idx:3d}. {song.display_name} -> {path}\n")
            f.write("\n")

        if skipped_songs:
            f.write("-" * 70 + "\n")
            f.write(f"SKIPPED TRACKS ({len(skipped_songs)}):\n")
            f.write("-" * 70 + "\n")
            for idx, (song, path) in enumerate(skipped_songs, start=1):
                f.write(f"{idx:3d}. {song.display_name} -> {path}\n")
            f.write("\n")

    # If there are failed songs, write a clean otofetch_failed.txt containing Spotify URLs
    if failed_songs:
        retry_file = log_path / "otofetch_failed.txt"
        with open(retry_file, "w", encoding="utf-8") as rf:
            for song, _ in failed_songs:
                if song.url:
                    rf.write(f"{song.url}\n")
                else:
                    rf.write(f"{song.display_name}\n")

    return report_file, retry_file
