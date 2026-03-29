from __future__ import annotations

import re

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


class TranscriptNotAvailable(Exception):
    pass


def _extract_video_id(url: str) -> str:
    """Extract YouTube video ID from a URL."""
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?/]|$)",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise TranscriptNotAvailable(f"Could not extract video ID from URL: {url}")


def fetch_transcript(url: str, language: str = "en") -> list[dict]:
    """Fetch the transcript for a YouTube video.

    Args:
        url: YouTube video URL.
        language: Preferred transcript language code (default: "en").

    Returns:
        List of transcript segments, each with keys:
        - text: str — the spoken text
        - start: float — start time in seconds
        - duration: float — duration in seconds

    Raises:
        TranscriptNotAvailable: If transcript cannot be fetched.
    """
    video_id = _extract_video_id(url)
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript([language, "en"])
        fetched = transcript.fetch()
        return [
            {"text": seg.text, "start": seg.start, "duration": seg.duration}
            for seg in fetched
        ]
    except (TranscriptsDisabled, VideoUnavailable) as exc:
        raise TranscriptNotAvailable(str(exc)) from exc
    except Exception as exc:
        raise TranscriptNotAvailable(
            f"Failed to fetch transcript for {url}: {exc}"
        ) from exc
