"""Model-driven intent decision components."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Type

from .prompts import build_system_prompt
from tinyllamax.core.intents import parse_intent, IntentParseError, IntentType
from tinyllamax.model_backends.interface import ModelBackend

JSON_PATTERN = re.compile(r"\{.*?\}", re.DOTALL)


class IntentDecider:
    """Orchestrates calling a model backend and parsing a single intent JSON."""

    def __init__(self, backend: ModelBackend) -> None:
        self.backend = backend
        self.system_prompt = build_system_prompt()

    def decide(self, user_text: str) -> IntentType:
        raw = self.backend.complete(system=self.system_prompt, user=user_text)
        if not raw:
            raise IntentParseError("Model returned empty output")
        cleaned = self._extract_json(raw)
        try:
            obj = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise IntentParseError("Invalid JSON from model", details={"raw": raw[:200]}) from e
        return parse_intent(obj)

    def _extract_json(self, text: str) -> str:
        """Return the first JSON object substring found in text or the text itself.

        Heuristics:
        - If fenced with ```...```, the regex still finds the first {..} object.
        - Returns the first balanced-looking object via non-greedy regex.
        """
        t = text.strip()
        match = JSON_PATTERN.search(t)
        if not match:
            return t  # maybe already JSON
        js = match.group(0)
        # Remove trailing content after the object
        # Basic heuristic: balance braces
        return js

__all__ = ["IntentDecider"]
