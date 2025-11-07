"""Adapter factory for package managers."""
from __future__ import annotations

from tinyllamax.adapters import AptAdapter, DnfAdapter, PacmanAdapter, ZypperAdapter, ApkAdapter
from tinyllamax.adapters.base import PackageManagerAdapter

_MAPPING: dict[str, type[PackageManagerAdapter]] = {
    "apt": AptAdapter,
    "dnf": DnfAdapter,
    "pacman": PacmanAdapter,
    "zypper": ZypperAdapter,
    "apk": ApkAdapter,
}


def get_adapter(pm: str, dry_run: bool) -> PackageManagerAdapter:
    cls = _MAPPING.get(pm)
    if cls is None:
        raise ValueError(f"Unsupported package manager: {pm}")
    return cls(dry_run=dry_run)

__all__ = ["get_adapter"]
