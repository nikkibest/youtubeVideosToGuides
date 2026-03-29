# CLAUDE.md — YouTube to Guides

## Project Overview

`ytguide` is a Python CLI tool that converts YouTube tutorial videos into structured, step-by-step Markdown guides with embedded screenshots. It fetches video metadata and transcripts, extracts representative frames, and uses Claude AI to produce a readable, organized document.

**Example use cases:**
- "How to learn handstand" video → step-by-step progression guide with images
- Fingerstyle guitar tutorial → structured document organized by song section

## Architecture

Stateless CLI tool — no frontend, backend, or database. Each run is independent.

```
ytguide/
├── cli.py         # Typer CLI entry point — `generate` command
├── video.py       # yt-dlp: metadata fetch + video download
├── transcript.py  # youtube-transcript-api: fetch transcript segments
├── images.py      # opencv: frame extraction + timestamp sampling
├── guide.py       # Claude API: prompt building + guide generation
├── templates.py   # GuideTemplate + Step dataclasses, Markdown rendering
├── output.py      # Save guide to disk
└── __init__.py
tests/
conductor/         # Conductor project context (product, tech-stack, workflow, tracks)
```

## CLI Usage

```bash
# Install
uv sync

# Run
ytguide generate <youtube-url>
ytguide generate <youtube-url> --output ./my-output

# Help
ytguide --help
```

Output is written to `output/` by default:
- `output/<title>.md` — the generated guide
- `output/frames/` — extracted video frames
- `output/video/` — downloaded video file

## Pipeline (6 steps)

1. **Metadata** — `fetch_metadata(url)` via yt-dlp
2. **Transcript** — `fetch_transcript(url)` via youtube-transcript-api (graceful fallback if unavailable)
3. **Download** — `download_video(url, dir)` via yt-dlp
4. **Frame extraction** — `sample_timestamps()` + `extract_frames()` via opencv (15 frames by default)
5. **Guide generation** — `generate_guide()` calls Claude (`claude-sonnet-4-6`) with transcript + frame timestamps → structured JSON → `GuideTemplate`
6. **Save** — `render()` → Markdown, written to disk by `save_guide()`

## Key Data Types

```python
# ytguide/templates.py
@dataclass
class Step:
    number: int
    title: str
    description: str
    image_path: Path | None
    timestamp: int | None

@dataclass
class GuideTemplate:
    title: str
    source_url: str
    uploader: str
    intro: str
    steps: list[Step]
    outro: str
```

## Environment

The `ANTHROPIC_API_KEY` environment variable must be set for guide generation (Step 5).

## Tech Stack

| Concern | Library |
|---|---|
| CLI | `typer` + `rich` |
| Video/metadata | `yt-dlp` |
| Transcripts | `youtube-transcript-api` |
| Frame extraction | `opencv-python`, `Pillow` |
| AI guide generation | `anthropic` (Claude API) |
| Linting/formatting | `ruff` |
| Testing | `pytest` |
| Package management | `uv` |

## Code Style

- **Formatter:** `ruff format` (line length 88, double quotes)
- **Linter:** `ruff check` (rules: E, F, I, UP)
- **Type hints** on all public functions; use `X | Y` not `Union[X, Y]`
- **Naming:** `snake_case` functions/variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, `_prefix` for private
- **Imports order:** stdlib → third-party → local, separated by blank lines
- `from __future__ import annotations` at top of every module
- Functions max ~30 lines; single responsibility
- Custom exception classes for domain errors (e.g. `TranscriptNotAvailable`, `VideoUnavailable`, `FrameExtractionError`)
- Raise early, return results at the end

## Workflow

- **Commits:** Conventional Commits — `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`
- **Tests:** Flexible TDD — write tests for complex/non-trivial logic (parsing, transformation, prompt logic); skip for simple CLI glue
- **Code review:** Required for non-trivial changes (new features, refactors, core logic)
- **Verification:** After each task, manually verify output and run relevant tests before marking complete

## Development Commands

```bash
uv sync                        # Install dependencies
uv run ytguide generate <url>  # Run CLI
uv run pytest                  # Run tests
uv run ruff check .            # Lint
uv run ruff format .           # Format
```

## Conductor Tracks

Active development uses the Conductor system. Track specs live in `conductor/tracks/`. Current track: `project-setup_20260323`.
