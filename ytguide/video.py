from __future__ import annotations

from pathlib import Path

import yt_dlp


class VideoUnavailable(Exception):
    pass


def fetch_metadata(url: str) -> dict:
    """Fetch video metadata without downloading.

    Args:
        url: YouTube video URL.

    Returns:
        Dict with keys: title, description, duration, chapters, uploader, upload_date.

    Raises:
        VideoUnavailable: If the video cannot be accessed.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "duration": info.get("duration", 0),
            "chapters": info.get("chapters") or [],
            "uploader": info.get("uploader", ""),
            "upload_date": info.get("upload_date", ""),
            "video_id": info.get("id", ""),
        }
    except yt_dlp.utils.DownloadError as exc:
        raise VideoUnavailable(f"Could not fetch metadata for {url}: {exc}") from exc


def download_video(url: str, output_dir: Path) -> Path:
    """Download a YouTube video to the given directory.

    Args:
        url: YouTube video URL.
        output_dir: Directory to save the downloaded video.

    Returns:
        Path to the downloaded video file.

    Raises:
        VideoUnavailable: If the video cannot be downloaded.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(id)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "outtmpl": output_template,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "")
            video_path = output_dir / f"{video_id}.mp4"
            if not video_path.exists():
                # fallback: find any mp4 in output_dir matching video_id
                matches = list(output_dir.glob(f"{video_id}.*"))
                if not matches:
                    raise VideoUnavailable("Downloaded file not found.")
                video_path = matches[0]
        return video_path
    except yt_dlp.utils.DownloadError as exc:
        raise VideoUnavailable(f"Could not download {url}: {exc}") from exc
