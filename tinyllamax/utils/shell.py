"""Shell execution helpers.

Provides safe run(cmd: list[str]) returning a result object and
summarize_output(...) utility used by planner.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import subprocess

@dataclass
class ShellResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    simulated: bool = False


def run(cmd: List[str]) -> ShellResult:
    """Run a command list safely (no shell=True) capturing output.

    On failure returns non-zero returncode with captured stderr/stdout.
    """
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return ShellResult(command=cmd, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except subprocess.TimeoutExpired:
        return ShellResult(command=cmd, returncode=-1, stdout="", stderr="TIMEOUT: command exceeded limit")
    except Exception as e:  # broad catch to avoid planner crashes
        return ShellResult(command=cmd, returncode=-1, stdout="", stderr=f"ERROR: {e}")


def summarize_output(stdout: str, stderr: str, max_lines: int = 10) -> str:
    """Return a concise summary using the tail of stdout/stderr limited by max_lines total."""
    out_lines = [l for l in stdout.strip().splitlines() if l.strip()]
    err_lines = [l for l in stderr.strip().splitlines() if l.strip()]
    combined = out_lines + (['--- STDERR ---'] + err_lines if err_lines else [])
    if len(combined) > max_lines:
        combined = combined[-max_lines:]
    return '\n'.join(combined) if combined else '<no output>'

__all__ = ["run", "ShellResult", "summarize_output"]
