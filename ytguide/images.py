from __future__ import annotations

from pathlib import Path

import cv2


class FrameExtractionError(Exception):
    pass


def extract_frames(
    video_path: Path,
    timestamps: list[float],
    output_dir: Path,
) -> list[Path]:
    """Extract frames from a video at the given timestamps.

    Args:
        video_path: Path to the video file.
        timestamps: List of timestamps in seconds to extract frames at.
        output_dir: Directory to save the extracted frame images.

    Returns:
        List of paths to the saved frame images (PNG format).

    Raises:
        FrameExtractionError: If the video cannot be opened or a frame cannot be read.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FrameExtractionError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    saved_paths: list[Path] = []

    try:
        for i, timestamp in enumerate(timestamps):
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                continue
            frame_path = output_dir / f"frame_{i:04d}_{int(timestamp):05d}s.png"
            cv2.imwrite(str(frame_path), frame)
            saved_paths.append(frame_path)
    finally:
        cap.release()

    return saved_paths


def sample_timestamps(duration: float, count: int = 10) -> list[float]:
    """Generate evenly-spaced timestamps across a video duration.

    Args:
        duration: Total video duration in seconds.
        count: Number of timestamps to generate.

    Returns:
        List of timestamps in seconds.
    """
    if duration <= 0 or count <= 0:
        return []
    step = duration / (count + 1)
    return [step * (i + 1) for i in range(count)]
