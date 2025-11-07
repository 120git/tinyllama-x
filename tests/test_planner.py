import types
from typing import List

import tinyllamax.core.planner as planner
from tinyllamax.core.intents import InstallPackage, UpdateSystem, ExplainCommand
from tinyllamax.utils.shell import ShellResult

# Monkeypatch pattern: replace shell_run in planner module

def fake_shell_run(cmd: List[str]) -> ShellResult:
    return ShellResult(command=cmd, returncode=0, stdout="line1\nline2", stderr="", simulated=False)


def test_build_plan_install():
    intent = InstallPackage(package="htop")
    plan = planner.build_plan(intent, distro_id="ubuntu")
    assert "Install package 'htop'" in plan.description
    assert plan.simulate_cmd[0] == "apt"  # dry-run uses non-sudo for apt
    assert plan.real_cmd[0] == "sudo"


def test_simulate_and_execute(monkeypatch):
    monkeypatch.setattr(planner, "shell_run", fake_shell_run, raising=True)
    # simulate
    intent = UpdateSystem()
    plan = planner.build_plan(intent, distro_id="ubuntu")
    sim = planner.simulate(plan)
    assert sim.result.command == plan.simulate_cmd
    assert "line2" in sim.summary
    # execute
    exe = planner.execute(plan)
    assert exe.result.command == plan.real_cmd


def test_explain_plan(monkeypatch):
    monkeypatch.setattr(planner, "shell_run", fake_shell_run, raising=True)
    intent = ExplainCommand(command="ls -la")
    plan = planner.build_plan(intent)
    assert plan.real_cmd is None
    sim = planner.simulate(plan)
    assert sim.plan.description.startswith("Explain command")
    exe = planner.execute(plan)
    assert exe.summary == "<no execution needed>"
