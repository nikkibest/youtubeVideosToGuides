from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Step:
    number: int
    title: str
    description: str
    image_path: Path | None = None
    timestamp: float | None = None


@dataclass
class GuideTemplate:
    title: str
    source_url: str
    intro: str
    steps: list[Step] = field(default_factory=list)
    outro: str = ""
    uploader: str = ""


def render(guide: GuideTemplate, images_relative_to: Path | None = None) -> str:
    """Render a GuideTemplate to a Markdown string.

    Args:
        guide: The guide data to render.
        images_relative_to: If provided, image paths are made relative to this directory.

    Returns:
        Markdown string.
    """
    lines: list[str] = []

    # Title
    lines.append(f"# {guide.title}")
    lines.append("")

    # Meta
    if guide.uploader:
        lines.append(f"> **Source:** [{guide.uploader}]({guide.source_url})")
    else:
        lines.append(f"> **Source:** {guide.source_url}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Introduction
    lines.append("## Introduction")
    lines.append("")
    lines.append(guide.intro)
    lines.append("")
    lines.append("---")
    lines.append("")

    # Steps
    lines.append("## Steps")
    lines.append("")
    for step in guide.steps:
        lines.append(f"### Step {step.number}: {step.title}")
        lines.append("")
        if step.image_path is not None:
            if images_relative_to is not None:
                try:
                    img_ref = step.image_path.relative_to(images_relative_to)
                except ValueError:
                    img_ref = step.image_path
            else:
                img_ref = step.image_path
            lines.append(f"![Step {step.number} — {step.title}]({img_ref})")
            lines.append("")
        lines.append(step.description)
        lines.append("")

    lines.append("---")
    lines.append("")

    # Outro
    if guide.outro:
        lines.append("## Summary")
        lines.append("")
        lines.append(guide.outro)
        lines.append("")

    return "\n".join(lines)
