from __future__ import annotations
from typing import List
from .base import PackageManagerAdapter

class AptAdapter(PackageManagerAdapter):
    def install(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["apt", "install", "-s", *packages]
        return ["sudo", "apt", "install", "-y", *packages]

    def remove(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["apt", "remove", "-s", *packages]
        return ["sudo", "apt", "remove", "-y", *packages]

    def update(self) -> List[str]:
        if self.dry_run:
            return ["apt", "update", "-s"]
        return ["sudo", "apt", "update"]

    def upgrade(self) -> List[str]:
        if self.dry_run:
            return ["apt", "upgrade", "-s"]
        return ["sudo", "apt", "upgrade", "-y"]

    def search(self, query: str) -> List[str]:
        return ["apt", "search", query]
