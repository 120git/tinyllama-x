"""Typer CLI entrypoint for tinyllamax.

Features:
  * Auto-detect distro & preferred package manager
  * Intent planning & simulation-first workflow
  * Risk / undo hint surface
  * Debug path: feed raw JSON intent ( --json )
"""
from __future__ import annotations

import json

import typer

from .adapters import ApkAdapter, AptAdapter, DnfAdapter, PacmanAdapter, ZypperAdapter
from .config import AppSettings
from .core.intents import (
    DetectDistro,
    ExplainCommand,
    InstallPackage,
    IntentParseError,
    IntentType,
    RemovePackage,
    SearchPackage,
    UpdateSystem,
    UpgradeSystem,
    parse_intent,
)
from .core.planner import build_plan, confirm, execute, simulate, run_intent
from .core.model import IntentDecider
from .model_backends.ollama import OllamaBackend
try:  # optional llama.cpp
    from .model_backends.llamacpp import LlamaCppBackend  # type: ignore
except Exception:  # pragma: no cover
    LlamaCppBackend = None  # type: ignore
from .core.prompts import build_system_prompt
from .core.rag import explain_command as rag_explain
from .utils.distro import parse_os_release, preferred_pkg_manager

app = typer.Typer(help="Tinyllamax intelligent CLI (simulation-first)")


RISK_HINTS = {
    InstallPackage: "Risk: package install may modify system state.",
    RemovePackage: "Risk: removing packages can break dependencies.",
    UpdateSystem: "Risk: updates could introduce new versions; review changes.",
    UpgradeSystem: "Risk: upgrades can be disruptive; ensure backups.",
    SearchPackage: "Low risk: read-only package metadata query.",
    ExplainCommand: "Low risk: explanation only, no execution.",
    DetectDistro: "Low risk: reads system metadata.",
}

UNDO_HINTS = {
    InstallPackage: "Undo: remove with your package manager (e.g. apt remove <pkg>).",
    RemovePackage: "Undo: reinstall the package if available (apt install <pkg>).",
    UpdateSystem: "Undo: limited; check /var/log/apt for reverted packages.",
    UpgradeSystem: "Undo: use snapshots/backup or downgrade manually.",
}


from typing import Optional


def _adapter_for(pm: str, dry_run: bool) -> Optional[object]:  # placeholder for future
    from .adapters.base import PackageManagerAdapter
    mapping: dict[str, type[PackageManagerAdapter]] = {
        "apt": AptAdapter,
        "dnf": DnfAdapter,
        "pacman": PacmanAdapter,
        "zypper": ZypperAdapter,
        "apk": ApkAdapter,
    }
    cls = mapping.get(pm)
    return cls(dry_run=dry_run) if cls else None


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging")) -> None:
    if verbose:
        typer.echo("[tinyllamax] Verbose mode enabled")


@app.command()
def settings() -> None:
    s = AppSettings()
    for field, value in s.model_dump().items():
        typer.echo(f"{field}: {value}")


@app.command()
def debug_intent(
    json_payload: str = typer.Option(..., "--json", help="Raw JSON intent payload"),
    distro_override: str | None = typer.Option(None, "--distro", help="Override distro id"),
    execute_real: bool = typer.Option(False, "--real", help="Execute real command after simulation"),
) -> None:
    """Feed a JSON intent directly and exercise full plan → simulate → (optional) execute."""
    try:
        data = json.loads(json_payload)
        intent = parse_intent(data)
    except (json.JSONDecodeError, IntentParseError) as e:
        typer.echo(f"Error parsing intent: {e}", err=True)
        raise typer.Exit(code=1) from None

    distro_id, version_id = parse_os_release()
    if distro_override:
        distro_id = distro_override
    plan = build_plan(intent, distro_id=distro_id)
    typer.echo(f"Intent: {intent.__class__.__name__}")
    typer.echo(f"Distro: {distro_id}")
    typer.echo(f"Description: {plan.description}")
    if plan.simulate_cmd:
        typer.echo(f"Simulate: {' '.join(plan.simulate_cmd)}")
    if plan.real_cmd:
        typer.echo(f"Real:     {' '.join(plan.real_cmd)}")
    typer.echo(RISK_HINTS.get(intent.__class__, ""))
    undo = UNDO_HINTS.get(intent.__class__)
    if undo:
        typer.echo(undo)

    # If it's an explanation intent, show merged TLDR + man content too
    if isinstance(intent, ExplainCommand):
        typer.echo("--- Explanation (tldr/man) ---")
        typer.echo(rag_explain(intent.command))

    sim = simulate(plan)
    typer.echo("--- Simulation Output (tail) ---")
    typer.echo(sim.summary)

    if execute_real and plan.real_cmd:
        if confirm("Execute real command? [Y/n]: "):
            res = execute(plan)
            typer.echo("--- Execution Output (tail) ---")
            typer.echo(res.summary)
        else:
            typer.echo("Aborted real execution.")
    else:
        typer.echo("(Real execution skipped; use --real to execute)")


@app.command()
def plan(
    install: str | None = typer.Option(None, help="Package to install"),
    remove: str | None = typer.Option(None, help="Package to remove"),
    search: str | None = typer.Option(None, help="Package query to search"),
    update: bool = typer.Option(False, help="Update package lists"),
    upgrade: bool = typer.Option(False, help="Upgrade packages"),
    explain: str | None = typer.Option(None, help="Explain a command"),
    real: bool = typer.Option(False, "--real", help="Execute real command after simulation"),
) -> None:
    """High-level wrapper building an intent from flags and performing simulation-first run."""
    provided = [bool(install), bool(remove), bool(search), update, upgrade, bool(explain)]
    if sum(1 for x in provided if x) != 1:
        typer.echo("Provide exactly one action flag (install/remove/search/update/upgrade/explain)", err=True)
        raise typer.Exit(code=1) from None

    # Determine intent
    intent: IntentType
    if install:
        intent = InstallPackage(package=install)
    elif remove:
        intent = RemovePackage(package=remove)
    elif search:
        intent = SearchPackage(query=search)
    elif update:
        intent = UpdateSystem()
    elif upgrade:
        intent = UpgradeSystem()
    elif explain:
        intent = ExplainCommand(command=explain)
    else:  # fallback (should not happen due to earlier check)
        intent = DetectDistro()

    distro_id, version_id = parse_os_release()
    pm = preferred_pkg_manager(distro_id)
    plan_obj = build_plan(intent, distro_id=distro_id)

    typer.echo(f"Intent: {intent.__class__.__name__}")
    typer.echo(f"Distro: {distro_id} ({version_id}) -> PM: {pm}")
    typer.echo(f"Description: {plan_obj.description}")
    if plan_obj.simulate_cmd:
        typer.echo(f"Simulate: {' '.join(plan_obj.simulate_cmd)}")
    if plan_obj.real_cmd:
        typer.echo(f"Real:     {' '.join(plan_obj.real_cmd)}")
    typer.echo(RISK_HINTS.get(intent.__class__, ""))
    undo = UNDO_HINTS.get(intent.__class__)
    if undo:
        typer.echo(undo)

    # For explain intent, also surface a richer merged explanation (TLDR + man) if available
    if isinstance(intent, ExplainCommand):
        typer.echo("--- Explanation (tldr/man) ---")
        typer.echo(rag_explain(intent.command))

    sim_res = simulate(plan_obj)
    typer.echo("--- Simulation Output (tail) ---")
    typer.echo(sim_res.summary)

    if real and plan_obj.real_cmd:
        if confirm("Execute real command? [Y/n]: "):
            exec_res = execute(plan_obj)
            typer.echo("--- Execution Output (tail) ---")
            typer.echo(exec_res.summary)
        else:
            typer.echo("Aborted real execution.")
    else:
        typer.echo("(Real execution skipped; use --real to execute)")


@app.command()
def chat(
    user_text: str = typer.Argument(..., help="Raw user text to classify into an intent"),
    backend: str = typer.Option("ollama", help="Backend to use: ollama|llamacpp"),
    model: str = typer.Option("tinyllama:latest", help="Model name or path (backend-specific)"),
    run_: bool = typer.Option(False, "--run", help="After simulation, confirm and execute real command if available"),
) -> None:
    """Model-driven intent classification → simulate (always) → optional confirm & execute.

    Default is simulation-only. Pass --run to attempt real execution (will prompt for confirmation).
    """
    # Instantiate backend
    if backend == "ollama":
        be = OllamaBackend(model=model)
    elif backend == "llamacpp":
        if LlamaCppBackend is None:
            typer.echo("llama.cpp backend unavailable (library not installed)", err=True)
            raise typer.Exit(code=1)
        be = LlamaCppBackend(model_path=model)
    else:
        typer.echo(f"Unknown backend '{backend}'", err=True)
        raise typer.Exit(code=1)

    decider = IntentDecider(be)
    try:
        intent = decider.decide(user_text)
    except Exception as e:
        typer.echo(f"Failed to decide intent: {e}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Model intent: {intent}")
    distro_id, _version_id = parse_os_release()
    # Always simulate first
    sim_res, _ = run_intent(intent, distro_id=distro_id, execute_real=False)
    typer.echo("--- Simulation Output (tail) ---")
    typer.echo(sim_res.summary)
    if run_:
        if sim_res.plan.real_cmd:
            if confirm("Execute real command? [Y/n]: "):
                exe_res = execute(sim_res.plan)
                typer.echo("--- Execution Output (tail) ---")
                typer.echo(exe_res.summary)
            else:
                typer.echo("Aborted real execution.")
        else:
            typer.echo("<no real execution needed for this intent>")
    else:
        typer.echo("(Real execution skipped; pass --run to attempt)")


if __name__ == "__main__":  # pragma: no cover
    app()