from __future__ import annotations

import json
from pathlib import Path

import anthropic

from ytguide.templates import GuideTemplate, Step


def _build_prompt(
    metadata: dict,
    transcript: list[dict],
    frames: list[Path],
) -> str:
    """Build the Claude prompt for guide generation."""
    transcript_text = "\n".join(
        f"[{seg['start']:.1f}s] {seg['text']}" for seg in transcript
    )
    chapters_text = ""
    if metadata.get("chapters"):
        chapters_text = "\nVideo chapters:\n" + "\n".join(
            f"  - {c['title']} ({c['start_time']:.0f}s – {c['end_time']:.0f}s)"
            for c in metadata["chapters"]
        )

    frame_times = [
        float(f.stem.split("_")[-1].rstrip("s")) for f in frames
    ]
    frames_text = "Available screenshot timestamps (seconds): " + ", ".join(
        str(t) for t in frame_times
    )

    return f"""You are creating a clear, structured, step-by-step tutorial guide from a YouTube video transcript.

Video title: {metadata['title']}
Channel: {metadata.get('uploader', 'Unknown')}
Duration: {metadata['duration']} seconds
{chapters_text}

{frames_text}

Full transcript:
{transcript_text}

---

Your task: Extract and structure all the steps taught in this video into a well-organized tutorial guide.

Return a JSON object with this exact structure:
{{
  "intro": "2-3 sentence introduction explaining what the viewer will learn and any prerequisites",
  "steps": [
    {{
      "number": 1,
      "title": "Short step title (3-6 words)",
      "description": "Clear, detailed description of this step (2-4 sentences). Include the key technique, common mistakes to avoid, and how long to practice.",
      "best_frame_timestamp": 25
    }}
  ],
  "outro": "2-3 sentence summary and encouragement for the reader"
}}

Rules:
- Extract every distinct step mentioned in the video (there should be 6-10 steps)
- For best_frame_timestamp, choose the timestamp (from the available list) that best shows this step being demonstrated
- Descriptions must be practical and actionable — someone reading this should be able to perform the step
- Keep titles concise and descriptive
- Return only the JSON object, no other text"""


def generate_guide(
    metadata: dict,
    transcript: list[dict],
    frames: list[Path],
    source_url: str,
) -> GuideTemplate:
    """Use Claude to generate a structured guide from video data.

    Args:
        metadata: Video metadata dict from fetch_metadata.
        transcript: Transcript segments from fetch_transcript.
        frames: List of extracted frame image paths.
        source_url: Original YouTube URL.

    Returns:
        A populated GuideTemplate ready to render.
    """
    client = anthropic.Anthropic()
    prompt = _build_prompt(metadata, transcript, frames)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    data = json.loads(raw)

    # Map best_frame_timestamp to the closest actual frame file
    frame_map: dict[int, Path] = {}
    for frame_path in frames:
        try:
            ts = int(frame_path.stem.split("_")[-1].rstrip("s"))
            frame_map[ts] = frame_path
        except (ValueError, IndexError):
            pass

    steps: list[Step] = []
    for s in data["steps"]:
        best_ts = s.get("best_frame_timestamp")
        matched_frame: Path | None = None
        if best_ts is not None and frame_map:
            closest_ts = min(frame_map.keys(), key=lambda t: abs(t - int(best_ts)))
            matched_frame = frame_map[closest_ts]

        steps.append(
            Step(
                number=s["number"],
                title=s["title"],
                description=s["description"],
                image_path=matched_frame,
                timestamp=best_ts,
            )
        )

    return GuideTemplate(
        title=metadata["title"],
        source_url=source_url,
        uploader=metadata.get("uploader", ""),
        intro=data["intro"],
        steps=steps,
        outro=data.get("outro", ""),
    )
