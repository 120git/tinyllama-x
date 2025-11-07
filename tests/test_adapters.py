import pytest

from tinyllamax.adapters import (
    AptAdapter,
    DnfAdapter,
    PacmanAdapter,
    ZypperAdapter,
    ApkAdapter,
)

@pytest.mark.parametrize(
    "adapter_cls, real_install, dry_install",
    [
        (AptAdapter, ["sudo", "apt", "install", "-y", "htop"], ["apt", "install", "-s", "htop"]),
        (DnfAdapter, ["sudo", "dnf", "install", "-y", "htop"], ["dnf", "install", "--assumeno", "htop"]),
        (PacmanAdapter, ["sudo", "pacman", "-S", "--noconfirm", "htop"], ["pacman", "-Sp", "htop"]),
        (ZypperAdapter, ["sudo", "zypper", "install", "-y", "htop"], ["zypper", "--dry-run", "install", "htop"]),
        (ApkAdapter, ["sudo", "apk", "add", "htop"], ["apk", "add", "--simulate", "htop"]),
    ],
)
def test_install_commands(adapter_cls, real_install, dry_install):
    assert adapter_cls(dry_run=False).install(["htop"]) == real_install
    assert adapter_cls(dry_run=True).install(["htop"]) == dry_install

@pytest.mark.parametrize(
    "adapter_cls, real_remove, dry_remove",
    [
        (AptAdapter, ["sudo", "apt", "remove", "-y", "htop"], ["apt", "remove", "-s", "htop"]),
        (DnfAdapter, ["sudo", "dnf", "remove", "-y", "htop"], ["dnf", "remove", "--assumeno", "htop"]),
        (PacmanAdapter, ["sudo", "pacman", "-R", "--noconfirm", "htop"], ["pacman", "-R", "--print", "htop"]),
        (ZypperAdapter, ["sudo", "zypper", "remove", "-y", "htop"], ["zypper", "--dry-run", "remove", "htop"]),
        (ApkAdapter, ["sudo", "apk", "del", "htop"], ["apk", "del", "--simulate", "htop"]),
    ],
)
def test_remove_commands(adapter_cls, real_remove, dry_remove):
    assert adapter_cls(dry_run=False).remove(["htop"]) == real_remove
    assert adapter_cls(dry_run=True).remove(["htop"]) == dry_remove

@pytest.mark.parametrize(
    "adapter_cls, real_update, dry_update",
    [
        (AptAdapter, ["sudo", "apt", "update"], ["apt", "update", "-s"]),
        (DnfAdapter, ["sudo", "dnf", "upgrade", "-y"], ["dnf", "upgrade", "--assumeno"]),
        (PacmanAdapter, ["sudo", "pacman", "-Syu", "--noconfirm"], ["pacman", "-Syu", "--print"]),
        (ZypperAdapter, ["sudo", "zypper", "update", "-y"], ["zypper", "--dry-run", "update"]),
        (ApkAdapter, ["sudo", "apk", "update"], ["apk", "update", "--simulate"]),
    ],
)
def test_update_commands(adapter_cls, real_update, dry_update):
    assert adapter_cls(dry_run=False).update() == real_update
    assert adapter_cls(dry_run=True).update() == dry_update

@pytest.mark.parametrize(
    "adapter_cls, real_upgrade, dry_upgrade",
    [
        (AptAdapter, ["sudo", "apt", "upgrade", "-y"], ["apt", "upgrade", "-s"]),
        (DnfAdapter, ["sudo", "dnf", "upgrade", "-y"], ["dnf", "upgrade", "--assumeno"]),
        (PacmanAdapter, ["sudo", "pacman", "-Syu", "--noconfirm"], ["pacman", "-Qu"]),
        (ZypperAdapter, ["sudo", "zypper", "update", "-y"], ["zypper", "--dry-run", "update"]),
        (ApkAdapter, ["sudo", "apk", "upgrade"], ["apk", "upgrade", "--simulate"]),
    ],
)
def test_upgrade_commands(adapter_cls, real_upgrade, dry_upgrade):
    assert adapter_cls(dry_run=False).upgrade() == real_upgrade
    assert adapter_cls(dry_run=True).upgrade() == dry_upgrade

@pytest.mark.parametrize(
    "adapter_cls, search_cmd",
    [
        (AptAdapter, ["apt", "search", "htop"]),
        (DnfAdapter, ["dnf", "search", "htop"]),
        (PacmanAdapter, ["pacman", "-Ss", "htop"]),
        (ZypperAdapter, ["zypper", "search", "htop"]),
        (ApkAdapter, ["apk", "search", "htop"]),
    ],
)
def test_search_commands(adapter_cls, search_cmd):
    assert adapter_cls(dry_run=False).search("htop") == search_cmd
    assert adapter_cls(dry_run=True).search("htop") == search_cmd
