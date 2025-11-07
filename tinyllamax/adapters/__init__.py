"""Adapter package for package manager command construction."""
from .apt import AptAdapter
from .dnf import DnfAdapter
from .pacman import PacmanAdapter
from .zypper import ZypperAdapter
from .apk import ApkAdapter

__all__ = [
    "AptAdapter",
    "DnfAdapter",
    "PacmanAdapter",
    "ZypperAdapter",
    "ApkAdapter",
]
