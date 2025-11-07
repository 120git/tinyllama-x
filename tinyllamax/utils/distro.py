"""Minimal Linux distribution detection utilities.

Provides:
  parse_os_release(path: str = "/etc/os-release") -> tuple[id, version_id]
  preferred_pkg_manager(distro_id: str) -> Literal["apt","dnf","pacman","zypper","apk","unknown"]

The parser follows the freedesktop.org os-release format.
Quotes around values are stripped. Missing keys yield "unknown".
"""
from __future__ import annotations

from typing import Literal, Tuple

_OS_RELEASE_DEFAULT_PATH = "/etc/os-release"

PkgManager = Literal["apt", "dnf", "pacman", "zypper", "apk", "unknown"]


def _parse_kv_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, value = line.split("=", 1)
    value = value.strip().strip('"').strip("'")
    return key, value


def parse_os_release(path: str = _OS_RELEASE_DEFAULT_PATH) -> Tuple[str, str]:
    """Parse an os-release file, returning (id, version_id).

    If either key is absent, returns "unknown" for that position.
    """
    id_val = "unknown"
    version_val = "unknown"
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                parsed = _parse_kv_line(raw)
                if not parsed:
                    continue
                key, value = parsed
                if key == "ID":
                    id_val = value.lower()
                elif key == "VERSION_ID":
                    version_val = value
    except FileNotFoundError:
        return id_val, version_val
    except OSError:
        return id_val, version_val
    return id_val, version_val


def parse_os_release_content(content: str) -> Tuple[str, str]:
    """Test helper: parse provided os-release content string.
    Mirrors parse_os_release logic without file IO."""
    id_val = "unknown"
    version_val = "unknown"
    for raw in content.splitlines():
        parsed = _parse_kv_line(raw)
        if not parsed:
            continue
        key, value = parsed
        if key == "ID":
            id_val = value.lower()
        elif key == "VERSION_ID":
            version_val = value
    return id_val, version_val


def preferred_pkg_manager(distro_id: str) -> PkgManager:
    """Return preferred package manager for a given distro id (lowercase).

    Unrecognized ids return "unknown".
    Recognizes common IDs (ubuntu, debian, fedora, arch, opensuse*, alpine).
    """
    d = distro_id.lower()
    if d in {"ubuntu", "debian", "pop", "linuxmint", "mint"}:
        return "apt"
    if d in {"fedora", "rhel", "centos", "alma", "rocky"}:
        return "dnf"
    if d in {"arch", "manjaro", "endeavouros"}:
        return "pacman"
    if d.startswith("opensuse") or d in {"suse", "sles"}:
        return "zypper"
    if d == "alpine":
        return "apk"
    return "unknown"

__all__ = [
    "parse_os_release",
    "parse_os_release_content",
    "preferred_pkg_manager",
    "PkgManager",
]
