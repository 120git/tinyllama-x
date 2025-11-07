from __future__ import annotations
from typing import List
from .base import PackageManagerAdapter

class DnfAdapter(PackageManagerAdapter):
    def install(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["dnf", "install", "--assumeno", *packages]
        return ["sudo", "dnf", "install", "-y", *packages]

    def remove(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["dnf", "remove", "--assumeno", *packages]
        return ["sudo", "dnf", "remove", "-y", *packages]

    def update(self) -> List[str]:
        # dnf upgrade is the common pattern
        if self.dry_run:
            return ["dnf", "upgrade", "--assumeno"]
        return ["sudo", "dnf", "upgrade", "-y"]

    def upgrade(self) -> List[str]:
        if self.dry_run:
            return ["dnf", "upgrade", "--assumeno"]
        return ["sudo", "dnf", "upgrade", "-y"]

    def search(self, query: str) -> List[str]:
        return ["dnf", "search", query]
