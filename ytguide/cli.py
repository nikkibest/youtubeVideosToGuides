from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    name="ytguide",
    help="Convert YouTube videos into structured step-by-step guides.",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    url: str = typer.Argument(..., help="YouTube video URL to convert into a guide"),
    output_dir: Path = typer.Option(
        Path("output"),
        "--output",
        "-o",
        help="Directory to save the generated guide",
    ),
) -> None:
    """Generate a structured guide from a YouTube video."""
    console.print("[bold green]YouTube to Guides[/bold green]")
    console.print(f"Processing: {url}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching video metadata...", total=None)
        # TODO: fetch_metadata(url) — Phase 3

        progress.add_task("Fetching transcript...", total=None)
        # TODO: fetch_transcript(url) — Phase 3

        progress.add_task("Downloading video...", total=None)
        # TODO: download_video(url, output_dir) — Phase 3

        progress.add_task("Extracting frames...", total=None)
        # TODO: extract_frames(...) — Phase 3

        progress.add_task("Generating guide...", total=None)
        # TODO: generate_guide(...) — Phase 4

    console.print("[bold green]Done![/bold green] Guide saved to:", output_dir)
