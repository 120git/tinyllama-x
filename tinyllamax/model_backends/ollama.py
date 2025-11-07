"""Ollama backend using the `ollama` CLI.

Invokes `ollama run <model> <prompt>` and returns raw stdout.
Never uses shell=True and degrades gracefully on errors.
"""
from __future__ import annotations

import subprocess
from typing import Optional

from .interface import ModelBackend


class OllamaBackend(ModelBackend):
    def __init__(self, model: str = "tinyllama:latest", timeout: int = 60) -> None:
        self.model = model
        self.timeout = timeout

    def complete(self, system: str, user: str) -> str:
        prompt = f"System:\n{system}\n\nUser:\n{user}\n\nAssistant:"
        try:
            proc = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if proc.returncode == 0 and proc.stdout:
                return proc.stdout.strip()
            return (proc.stdout or "").strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""
        except Exception:
            return ""


__all__ = ["OllamaBackend"]
