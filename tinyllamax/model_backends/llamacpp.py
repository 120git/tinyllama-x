"""Optional llama.cpp backend using llama-cpp-python.

Provides a thin wrapper around llama_cpp.Llama. If the library or model
fails to load, completion returns an empty string.
"""
from __future__ import annotations

from typing import Optional

try:
    from llama_cpp import Llama  # pragma: no cover
except Exception:  # pragma: no cover
    Llama = None

from .interface import ModelBackend


class LlamaCppBackend(ModelBackend):
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        self._llm: Optional["Llama"] = None
        if Llama is not None:
            try:
                self._llm = Llama(model_path=model_path, n_ctx=n_ctx)
            except Exception:
                self._llm = None
        self.temperature = temperature

    def complete(self, system: str, user: str) -> str:
        if not self._llm:
            return ""
        prompt = f"System:\n{system}\n\nUser:\n{user}\n\nAssistant:"
        try:
            out = self._llm(prompt=prompt, temperature=self.temperature, max_tokens=512)
            # ensure dictionary-like
            if isinstance(out, dict):
                choices = out.get("choices")
                if isinstance(choices, list) and choices:
                    text = choices[0].get("text", "")
                    if isinstance(text, str):
                        return text.strip()
            return ""
        except Exception:
            return ""


__all__ = ["LlamaCppBackend"]
