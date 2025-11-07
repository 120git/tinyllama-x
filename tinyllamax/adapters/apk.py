from __future__ import annotations
from typing import List
from .base import PackageManagerAdapter

class ApkAdapter(PackageManagerAdapter):
    def install(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["apk", "add", "--simulate", *packages]
        return ["sudo", "apk", "add", *packages]

    def remove(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["apk", "del", "--simulate", *packages]
        return ["sudo", "apk", "del", *packages]

    def update(self) -> List[str]:
        if self.dry_run:
            return ["apk", "update", "--simulate"]
        return ["sudo", "apk", "update"]

    def upgrade(self) -> List[str]:
        if self.dry_run:
            return ["apk", "upgrade", "--simulate"]
        return ["sudo", "apk", "upgrade"]

    def search(self, query: str) -> List[str]:
        return ["apk", "search", query]
