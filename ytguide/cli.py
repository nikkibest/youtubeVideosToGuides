from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ytguide.images import FrameExtractionError, extract_frames, sample_timestamps
from ytguide.transcript import TranscriptNotAvailable, fetch_transcript
from ytguide.video import VideoUnavailable, download_video, fetch_metadata

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
        transient=False,
    ) as progress:
        # Step 1: Metadata
        task = progress.add_task("Fetching video metadata...", total=None)
        try:
            metadata = fetch_metadata(url)
        except VideoUnavailable as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1)
        progress.update(task, description=f"[green]✓[/green] {metadata['title']}")
        progress.stop_task(task)

        # Step 2: Transcript
        task = progress.add_task("Fetching transcript...", total=None)
        try:
            transcript = fetch_transcript(url)
        except TranscriptNotAvailable as exc:
            console.print(f"[yellow]Warning:[/yellow] {exc}")
            transcript = []
        progress.update(
            task,
            description=f"[green]✓[/green] Transcript: {len(transcript)} segments",
        )
        progress.stop_task(task)

        # Step 3: Download video
        video_dir = output_dir / "video"
        task = progress.add_task("Downloading video...", total=None)
        try:
            video_path = download_video(url, video_dir)
        except VideoUnavailable as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1)
        progress.update(
            task,
            description=f"[green]✓[/green] Downloaded: {video_path.name}",
        )
        progress.stop_task(task)

        # Step 4: Extract frames
        frames_dir = output_dir / "frames"
        task = progress.add_task("Extracting frames...", total=None)
        try:
            timestamps = sample_timestamps(metadata["duration"], count=10)
            frames = extract_frames(video_path, timestamps, frames_dir)
        except FrameExtractionError as exc:
            console.print(f"[yellow]Warning:[/yellow] {exc}")
            frames = []
        progress.update(
            task,
            description=f"[green]✓[/green] Extracted {len(frames)} frames",
        )
        progress.stop_task(task)

        # Step 5: Guide generation (Phase 4)
        task = progress.add_task("Generating guide...", total=None)
        # TODO: generate_guide(metadata, transcript, frames, output_dir) — Phase 4
        progress.update(
            task,
            description="[dim]Guide generation coming in next phase[/dim]",
        )
        progress.stop_task(task)

    console.print(f"\n[bold green]Done![/bold green] Output directory: {output_dir}")
    console.print(f"  Title:    {metadata['title']}")
    console.print(f"  Duration: {metadata['duration']}s")
    console.print(f"  Segments: {len(transcript)}")
    console.print(f"  Frames:   {len(frames)}")
