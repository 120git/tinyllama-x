from __future__ import annotations
from typing import List
from .base import PackageManagerAdapter

class PacmanAdapter(PackageManagerAdapter):
    def install(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["pacman", "-Sp", *packages]
        return ["sudo", "pacman", "-S", "--noconfirm", *packages]

    def remove(self, packages: List[str]) -> List[str]:
        if self.dry_run:
            return ["pacman", "-R", "--print", *packages]
        return ["sudo", "pacman", "-R", "--noconfirm", *packages]

    def update(self) -> List[str]:
        if self.dry_run:
            return ["pacman", "-Syu", "--print"]
        return ["sudo", "pacman", "-Syu", "--noconfirm"]

    def upgrade(self) -> List[str]:
        if self.dry_run:
            # list upgradeable packages
            return ["pacman", "-Qu"]
        return ["sudo", "pacman", "-Syu", "--noconfirm"]

    def search(self, query: str) -> List[str]:
        return ["pacman", "-Ss", query]
