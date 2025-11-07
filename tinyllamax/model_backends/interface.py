"""Model backend interface for intent decision.

Defines a minimal protocol for backends that can produce text completions
from a system + user prompt pair.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ModelBackend(ABC):
    """Abstract model backend.

    Implementations must return a raw text completion. Any errors should be
    handled internally and return an empty string rather than raising.
    """

    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        """Return a raw text completion.

        Parameters:
            system: System instruction string
            user:   User text input
        Returns:
            Raw model output string (may be empty on failure).
        """
        raise NotImplementedError


__all__ = ["ModelBackend"]
