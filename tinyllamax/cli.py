"""Typer CLI entrypoint for tinyllamax."""

import typer

from .config import AppSettings
from .models import CommandExplain, PackageAction

app = typer.Typer(help="TinyllamaX auxiliary CLI")

@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging")) -> None:
    """Root callback setting verbosity."""
    if verbose:
        typer.echo("[tinyllamax] Verbose mode enabled")

@app.command()
def settings() -> None:
    """Show resolved application settings."""
    s = AppSettings()
    for field, value in s.dict().items():
        typer.echo(f"{field}: {value}")

@app.command()
def explain(command: str, detail: int = typer.Option(1, min=1, max=3, help="Detail level (1-3)")) -> None:
    """Explain a shell command (placeholder)."""
    ce = CommandExplain(command=command, detail_level=detail)
    typer.echo(f"Explain: {ce.command} (detail {ce.detail_level}) -> [placeholder]")

@app.command()
def pkg(action: str, packages: str | None = typer.Option(None, help="Comma-separated package list")) -> None:
    """Perform a package action (placeholder)."""
    pkgs = packages.split(",") if packages else []
    pa = PackageAction(action=action, packages=pkgs)
    typer.echo(f"Package action: {pa.action} on {pa.packages or '[none]'} (placeholder)")

if __name__ == "__main__":  # pragma: no cover
    app()