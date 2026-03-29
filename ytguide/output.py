from __future__ import annotations

import re
from pathlib import Path


def _sanitize_filename(title: str) -> str:
    """Convert a title string into a safe filename."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug[:80] or "guide"


def save_guide(content: str, output_dir: Path, title: str) -> Path:
    """Write a Markdown guide to disk.

    Args:
        content: Markdown content to write.
        output_dir: Directory to save the file in.
        title: Guide title used to generate the filename.

    Returns:
        Path to the saved Markdown file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = _sanitize_filename(title) + ".md"
    guide_path = output_dir / filename
    guide_path.write_text(content, encoding="utf-8")
    return guide_path
