"""Execution planner for tinyllamax intents.

Builds human-readable plans and exact simulate/real command arrays
using adapters and distro utils, then executes via shell helpers.
"""
from __future__ import annotations

from dataclasses import dataclass

from tinyllamax.adapters import ApkAdapter, AptAdapter, DnfAdapter, PacmanAdapter, ZypperAdapter
from tinyllamax.adapters.base import PackageManagerAdapter
from tinyllamax.core.history import log_operation
from tinyllamax.core.intents import (
    DetectDistro,
    ExplainCommand,
    InstallPackage,
    IntentType,
    RemovePackage,
    SearchPackage,
    UpdateSystem,
    UpgradeSystem,
)
from tinyllamax.utils.distro import preferred_pkg_manager
from tinyllamax.utils.shell import ShellResult, summarize_output
from tinyllamax.utils.shell import run as shell_run


@dataclass
class Plan:
    description: str
    simulate_cmd: list[str] | None
    real_cmd: list[str] | None


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


def build_plan(intent: IntentType, distro_id: str | None = None) -> Plan:
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
    
    # Log simulation to history (best effort, don't fail if history unavailable)
    try:
        cmd_str = ' '.join(plan.simulate_cmd) if plan.simulate_cmd else ""
        log_operation(
            intent_type=plan.description.split()[0],  # Extract intent name from description
            command=cmd_str,
            status="simulated",
            output_summary=summary[:200]  # Truncate to reasonable length
        )
    except Exception:
        # Silently ignore history logging errors
        pass
    
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
    result: ShellResult | None
    summary: str


def execute(plan: Plan) -> ExecutionResult:
    """Execute the real command (if any) and summarize next steps."""
    if not plan.real_cmd:
        return ExecutionResult(plan=plan, result=None, summary="<no execution needed>")
    res = shell_run(plan.real_cmd)
    summary = summarize_output(res.stdout, res.stderr)
    
    # Log execution to history (best effort, don't fail if history unavailable)
    try:
        cmd_str = ' '.join(plan.real_cmd) if plan.real_cmd else ""
        status = "success" if res.returncode == 0 else "failed"
        error_msg = res.stderr[:500] if res.returncode != 0 and res.stderr else None
        
        log_operation(
            intent_type=plan.description.split()[0],  # Extract intent name from description
            command=cmd_str,
            status=status,
            output_summary=summary[:200],  # Truncate to reasonable length
            error_message=error_msg
        )
    except Exception:
        # Silently ignore history logging errors
        pass
    
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


def run_intent(intent: IntentType, distro_id: str | None = None, execute_real: bool = False) -> tuple[SimulationResult, ExecutionResult | None]:
    """Helper to build a plan, run simulation, and optionally execute.

    Returns a tuple of (simulation_result, execution_result_or_none).
    """
    plan = build_plan(intent, distro_id=distro_id)
    sim = simulate(plan)
    exe: ExecutionResult | None = None
    if execute_real and plan.real_cmd:
        exe = execute(plan)
    return sim, exe

