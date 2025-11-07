from __future__ import annotations
from typing import List
from .base import PackageManagerAdapter

class ZypperAdapter(PackageManagerAdapter):
    def install(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["zypper", "--dry-run", "install", *packages]
        return ["sudo", "zypper", "install", "-y", *packages]

    def remove(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["zypper", "--dry-run", "remove", *packages]
        return ["sudo", "zypper", "remove", "-y", *packages]

    def update(self) -> List[str]:
        if self.dry_run:
            return ["zypper", "--dry-run", "update"]
        return ["sudo", "zypper", "update", "-y"]

    def upgrade(self) -> List[str]:
        if self.dry_run:
            return ["zypper", "--dry-run", "update"]
        return ["sudo", "zypper", "update", "-y"]

    def search(self, query: str) -> List[str]:
        return ["zypper", "search", query]
