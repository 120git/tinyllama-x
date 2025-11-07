"""RAG-like helpers for explaining commands using local TLDR and man pages.

This module provides three functions:
- tldr(cmd): best-effort TLDR page fetch for the base command
- man_snippet(cmd, section=None, max_chars=800): short snippet of the man page
- explain_command(cmd): merged, readable explanation using TLDR then man

Design goals:
- Never raise on missing tools; return empty strings on failure
- Be safe and fast, no shell=True; limit output size
- Keep return types simple (plain strings)
"""
from __future__ import annotations

from typing import Optional
import os
import shlex
import subprocess


def _base_command(cmd: str) -> str:
    """Extract the base executable name from a command string.

    Example: "ls -la /tmp" -> "ls"
    """
    if not cmd or not isinstance(cmd, str):
        return ""
    try:
        parts = shlex.split(cmd)
    except ValueError:
        # Fallback: naive split
        parts = cmd.strip().split()
    return parts[0] if parts else ""


def tldr(cmd: str) -> str:
    """Return TLDR content for the base command, or empty string if unavailable.

    Implementation notes:
    - Uses "tldr <base>"; ignores flags/args
    - Gracefully handles FileNotFoundError (tldr not installed)
    - Returns stdout on success when returncode == 0, else empty string
    """
    base = _base_command(cmd)
    if not base:
        return ""
    try:
        proc = subprocess.run(["tldr", base], capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()
    except FileNotFoundError:
        # tldr not installed
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""
    return ""


def man_snippet(cmd: str, section: Optional[str] = None, max_chars: int = 800) -> str:
    """Return a short snippet of the man page for the base command.

    Behavior:
    - Runs: env PAGER=cat MANWIDTH=80 man [section] <base>
    - Returns trimmed stdout up to max_chars, or empty string if not available
    - If man is missing or errors/timeout occur, returns empty string
    """
    base = _base_command(cmd)
    if not base:
        return ""

    env = os.environ.copy()
    env["PAGER"] = "cat"
    env.setdefault("MANWIDTH", "80")

    man_cmd = ["man"] + ([section] if section else []) + [base]
    try:
        proc = subprocess.run(man_cmd, capture_output=True, text=True, timeout=15, env=env)
        if proc.returncode != 0 or not proc.stdout:
            return ""
        text = proc.stdout.strip()
        # Some systems include backspaces for bold/underline. Remove common artifacts.
        text = text.replace("\b", "")
        if len(text) > max_chars:
            text = text[: max_chars - 3].rstrip() + "..."
        return text
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""


def explain_command(cmd: str) -> str:
    """Combine TLDR and man snippet into a human-friendly explanation string.

    Order of preference: TLDR first, then a short man snippet. If neither is
    available, returns a short fallback string.
    """
    tl = tldr(cmd)
    mn = man_snippet(cmd)

    if tl and mn:
        return f"TLDR\n\n{tl}\n\nMan snippet\n\n{mn}"
    if tl:
        return tl
    if mn:
        return mn
    return "No explanation available. Install 'tldr' or ensure 'man' pages are present."


__all__ = ["tldr", "man_snippet", "explain_command"]
