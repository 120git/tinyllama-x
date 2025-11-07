"""Abstract base for package manager adapters.

Each method returns a command array (list[str]) ready for execution.
If dry_run is True, adapters will incorporate simulation flags where available.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

class PackageManagerAdapter(ABC):
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    @abstractmethod
    def install(self, packages: List[str]) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def remove(self, packages: List[str]) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def update(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def upgrade(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> List[str]:
        raise NotImplementedError

__all__ = ["PackageManagerAdapter"]
