"""Execution planner for tinyllamax intents.

Builds human-readable plans and exact simulate/real command arrays
using adapters and distro utils, then executes via shell helpers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from tinyllamax.core.intents import (
    IntentType,
    InstallPackage,
    RemovePackage,
    UpdateSystem,
    UpgradeSystem,
    SearchPackage,
    DetectDistro,
    ExplainCommand,
)
from tinyllamax.utils.distro import preferred_pkg_manager
from tinyllamax.adapters import AptAdapter, DnfAdapter, PacmanAdapter, ZypperAdapter, ApkAdapter
from tinyllamax.adapters.base import PackageManagerAdapter
from tinyllamax.utils.shell import run as shell_run, summarize_output, ShellResult


@dataclass
class Plan:
    description: str
    simulate_cmd: Optional[List[str]]
    real_cmd: Optional[List[str]]


def _get_adapter(pm: str, dry_run: bool) -> PackageManagerAdapter:
    mapping: dict[str, type[PackageManagerAdapter]] = {
        "apt": AptAdapter,
        "dnf": DnfAdapter,
        "pacman": PacmanAdapter,
        "zypper": ZypperAdapter,
        "apk": ApkAdapter,
    }
    adapter_cls = mapping.get(pm)
    if adapter_cls is None:
        raise ValueError(f"Unsupported package manager: {pm}")
    return adapter_cls(dry_run=dry_run)


def build_plan(intent: IntentType, distro_id: Optional[str] = None) -> Plan:
    """Construct a plan (description + simulate/real commands) for an intent.

    distro_id can be supplied to override detection; it's used to choose the adapter.
    """
    if isinstance(intent, DetectDistro):
        return Plan(
            description="Detect Linux distribution and version",
            simulate_cmd=["cat", "/etc/os-release"],
            real_cmd=None,
        )

    if isinstance(intent, SearchPackage):
        if not distro_id:
            distro_id = "ubuntu"  # default assumption
        pm = preferred_pkg_manager(distro_id)
        adapter = _get_adapter(pm, dry_run=False)
        dry_adapter = _get_adapter(pm, dry_run=True)
        return Plan(
            description=f"Search for package '{intent.query}' using {pm}",
            simulate_cmd=dry_adapter.search(intent.query),
            real_cmd=adapter.search(intent.query),
        )

    if isinstance(intent, InstallPackage):
        if not distro_id:
            distro_id = "ubuntu"
        pm = preferred_pkg_manager(distro_id)
        adapter = _get_adapter(pm, dry_run=False)
        dry_adapter = _get_adapter(pm, dry_run=True)
        return Plan(
            description=f"Install package '{intent.package}' using {pm}",
            simulate_cmd=dry_adapter.install([intent.package]),
            real_cmd=(adapter.install([intent.package]) if intent.assume_yes else adapter.install([intent.package])),
        )

    if isinstance(intent, RemovePackage):
        if not distro_id:
            distro_id = "ubuntu"
        pm = preferred_pkg_manager(distro_id)
        adapter = _get_adapter(pm, dry_run=False)
        dry_adapter = _get_adapter(pm, dry_run=True)
        return Plan(
            description=f"Remove package '{intent.package}' using {pm}",
            simulate_cmd=dry_adapter.remove([intent.package]),
            real_cmd=adapter.remove([intent.package]),
        )

    if isinstance(intent, UpdateSystem):
        if not distro_id:
            distro_id = "ubuntu"
        pm = preferred_pkg_manager(distro_id)
        adapter = _get_adapter(pm, dry_run=False)
        dry_adapter = _get_adapter(pm, dry_run=True)
        return Plan(
            description=f"Update system package lists ({pm})",
            simulate_cmd=dry_adapter.update(),
            real_cmd=adapter.update(),
        )

    if isinstance(intent, UpgradeSystem):
        if not distro_id:
            distro_id = "ubuntu"
        pm = preferred_pkg_manager(distro_id)
        adapter = _get_adapter(pm, dry_run=False)
        dry_adapter = _get_adapter(pm, dry_run=True)
        return Plan(
            description=f"Upgrade installed packages ({pm})",
            simulate_cmd=dry_adapter.upgrade(),
            real_cmd=adapter.upgrade(),
        )

    if isinstance(intent, ExplainCommand):
        return Plan(
            description=f"Explain command: {intent.command}",
            simulate_cmd=["bash", "-lc", f"type {intent.command.split()[0]} || true"],
            real_cmd=None,
        )

    # Fallback - should not reach here due to exhaustive union use
    raise ValueError(f"Unsupported intent type: {type(intent).__name__}")


@dataclass
class SimulationResult:
    plan: Plan
    result: ShellResult
    summary: str


def simulate(plan: Plan) -> SimulationResult:
    """Run the simulate_cmd (if any) and summarize output."""
    if not plan.simulate_cmd:
        res = ShellResult(command=[], returncode=0, stdout="", stderr="", simulated=True)
        return SimulationResult(plan=plan, result=res, summary="<nothing to simulate>")
    res = shell_run(plan.simulate_cmd)
    res.simulated = True
    summary = summarize_output(res.stdout, res.stderr)
    return SimulationResult(plan=plan, result=res, summary=summary)


def confirm(prompt: str = "Proceed? [Y/n]: ") -> bool:
    try:
        ans = input(prompt).strip().lower()
        return ans in {"", "y", "yes"}
    except EOFError:
        return False


@dataclass
class ExecutionResult:
    plan: Plan
    result: Optional[ShellResult]
    summary: str


def execute(plan: Plan) -> ExecutionResult:
    """Execute the real command (if any) and summarize next steps."""
    if not plan.real_cmd:
        return ExecutionResult(plan=plan, result=None, summary="<no execution needed>")
    res = shell_run(plan.real_cmd)
    summary = summarize_output(res.stdout, res.stderr)
    return ExecutionResult(plan=plan, result=res, summary=summary)

__all__ = [
    "Plan",
    "SimulationResult",
    "ExecutionResult",
    "build_plan",
    "simulate",
    "confirm",
    "execute",
]


def run_intent(intent: IntentType, distro_id: Optional[str] = None, execute_real: bool = False) -> tuple[SimulationResult, Optional[ExecutionResult]]:
    """Helper to build a plan, run simulation, and optionally execute.

    Returns a tuple of (simulation_result, execution_result_or_none).
    """
    plan = build_plan(intent, distro_id=distro_id)
    sim = simulate(plan)
    exe: Optional[ExecutionResult] = None
    if execute_real and plan.real_cmd:
        exe = execute(plan)
    return sim, exe

