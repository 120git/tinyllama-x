#!/usr/bin/env python3
"""
Validate package manager adapters' dry-run behavior for Fedora (dnf) and Arch (pacman)
without requiring those package managers to be installed.

We monkeypatch the adapter's _execute method to avoid running subprocesses and to
capture the constructed command strings for verification.

Exit codes:
  0 = PASS
  1 = FAIL (prints details)
"""

from typing import List, Optional
import sys

import os
import importlib

# Ensure project root is on sys.path when invoked directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from lib.pm_adapter import DnfAdapter, PacmanAdapter, CommandResult


def fake_execute(self, cmd: List[str], simulate_flag: Optional[str] = None) -> CommandResult:
    """Fake executor that mimics dry-run preview and returns the command string."""
    # Simulate how base class would append simulate_flag
    if getattr(self, 'dry_run', False) and simulate_flag:
        cmd = cmd + [simulate_flag]
    cmd_str = ' '.join(cmd)
    return CommandResult(
        success=True,
        command=cmd_str,
        stdout=f"[FAKE EXEC] {cmd_str}",
        stderr="",
        returncode=0,
        dry_run=getattr(self, 'dry_run', False),
    )


def assert_in(text: str, substr: str, ctx: str):
    if substr not in text:
        raise AssertionError(f"Expected '{substr}' in '{text}' ({ctx})")


def assert_not_in(text: str, substr: str, ctx: str):
    if substr in text:
        raise AssertionError(f"Did not expect '{substr}' in '{text}' ({ctx})")


def test_dnf():
    DnfAdapter._execute = fake_execute  # type: ignore
    dnf = DnfAdapter(dry_run=True)

    r = dnf.install(["htop"])  # should include --assumeno and no -y
    assert_in(r.command, "dnf install", "dnf install")
    assert_in(r.command, "--assumeno", "dnf install dry-run flag")
    assert_not_in(r.command, "-y", "dnf install drop -y in dry-run")

    r = dnf.remove(["htop"])  # should include --assumeno and no -y
    assert_in(r.command, "dnf remove", "dnf remove")
    assert_in(r.command, "--assumeno", "dnf remove dry-run flag")
    assert_not_in(r.command, "-y", "dnf remove drop -y in dry-run")

    r = dnf.update()  # should include --assumeno and no -y
    assert_in(r.command, "dnf upgrade", "dnf update")
    assert_in(r.command, "--assumeno", "dnf update dry-run flag")
    assert_not_in(r.command, "-y", "dnf update drop -y in dry-run")

    r = dnf.search("htop")
    assert_in(r.command, "dnf search htop", "dnf search")


def test_pacman():
    PacmanAdapter._execute = fake_execute  # type: ignore
    pac = PacmanAdapter(dry_run=True)

    r = pac.install(["htop"])  # should replace --noconfirm with --print
    assert_in(r.command, "pacman -S", "pacman install")
    assert_in(r.command, "--print", "pacman install print preview")
    assert_not_in(r.command, "--noconfirm", "pacman install drop noconfirm in dry-run")

    r = pac.remove(["htop"])  # should replace --noconfirm with --print
    assert_in(r.command, "pacman -R", "pacman remove")
    assert_in(r.command, "--print", "pacman remove print preview")
    assert_not_in(r.command, "--noconfirm", "pacman remove drop noconfirm in dry-run")

    r = pac.update()  # should use 'pacman -Qu' listing upgrades
    assert_in(r.command, "pacman -Qu", "pacman update dry-run uses -Qu")

    r = pac.search("htop")
    assert_in(r.command, "pacman -Ss htop", "pacman search")


def main() -> int:
    try:
        test_dnf()
        test_pacman()
        print("DRY-RUN VALIDATION: PASS (dnf + pacman)")
        return 0
    except AssertionError as e:
        print(f"DRY-RUN VALIDATION: FAIL -> {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
