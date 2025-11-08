"""Pure Python presenter/coordinator for the GUI.

Coordinates between the GUI view and the tinyllamax domain logic without
any GTK dependencies. Handles intent classification, planning, simulation,
and execution workflows.
"""
from __future__ import annotations

from collections.abc import Callable

from tinyllamax.core.history import OperationRecord, get_history
from tinyllamax.core.intents import IntentType
from tinyllamax.core.model import IntentDecider
from tinyllamax.core.planner import (
    ExecutionResult,
    Plan,
    SimulationResult,
    build_plan,
    execute,
    simulate,
)
from tinyllamax.core.rag import explain_command
from tinyllamax.model_backends.interface import ModelBackend
from tinyllamax.utils.distro import parse_os_release, preferred_pkg_manager


class TinyLlamaPresenter:
    """Coordinator between GUI and core tinyllamax functionality."""
    
    def __init__(self, backend: ModelBackend) -> None:
        """Initialize presenter with a model backend.
        
        Args:
            backend: Model backend for intent classification
        """
        self.backend = backend
        self.decider = IntentDecider(backend)
        self.current_intent: IntentType | None = None
        self.current_plan: Plan | None = None
        self.distro_id: str = "unknown"
        self.distro_version: str = "unknown"
        self.pkg_manager: str = "unknown"
        
        # Callbacks for UI updates
        self.on_status_update: Callable[[str], None] | None = None
        self.on_output_update: Callable[[str], None] | None = None
        self.on_plan_update: Callable[[str], None] | None = None
        self.on_error: Callable[[str], None] | None = None
        
        self._detect_system()
    
    def _detect_system(self) -> None:
        """Detect system distribution and package manager."""
        try:
            self.distro_id, self.distro_version = parse_os_release()
            self.pkg_manager = preferred_pkg_manager(self.distro_id)
            if self.on_status_update:
                self.on_status_update(
                    f"System: {self.distro_id} {self.distro_version} | PM: {self.pkg_manager}"
                )
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to detect system: {e}")
    
    def classify_intent(self, user_text: str) -> IntentType:
        """Classify user text into an intent using the model.
        
        Args:
            user_text: Raw user input text
            
        Returns:
            Classified intent
            
        Raises:
            Exception: If intent classification fails
        """
        if self.on_status_update:
            self.on_status_update("Classifying intent...")
        
        intent = self.decider.decide(user_text)
        self.current_intent = intent
        
        if self.on_status_update:
            self.on_status_update(f"Intent: {intent.__class__.__name__}")
        
        return intent
    
    def plan_intent(self, intent: IntentType) -> Plan:
        """Build a plan for the given intent.
        
        Args:
            intent: Intent to plan for
            
        Returns:
            Execution plan
        """
        if self.on_status_update:
            self.on_status_update("Building plan...")
        
        plan = build_plan(intent, distro_id=self.distro_id)
        self.current_plan = plan
        
        # Update plan display
        plan_text = f"Description: {plan.description}\n"
        if plan.simulate_cmd:
            plan_text += f"Simulate: {' '.join(plan.simulate_cmd)}\n"
        if plan.real_cmd:
            plan_text += f"Real: {' '.join(plan.real_cmd)}\n"
        
        if self.on_plan_update:
            self.on_plan_update(plan_text)
        
        if self.on_status_update:
            self.on_status_update("Plan ready")
        
        return plan
    
    def simulate_plan(self, plan: Plan) -> SimulationResult:
        """Simulate the execution plan.
        
        Args:
            plan: Plan to simulate
            
        Returns:
            Simulation result
        """
        if self.on_status_update:
            self.on_status_update("Running simulation...")
        
        result = simulate(plan)
        
        # Update output console
        output_text = f"=== Simulation ===\n{result.summary}\n"
        if self.on_output_update:
            self.on_output_update(output_text)
        
        if self.on_status_update:
            self.on_status_update("Simulation complete")
        
        return result
    
    def execute_plan(self, plan: Plan) -> ExecutionResult:
        """Execute the real command.
        
        Args:
            plan: Plan to execute
            
        Returns:
            Execution result
        """
        if self.on_status_update:
            self.on_status_update("Executing command...")
        
        result = execute(plan)
        
        # Update output console
        output_text = f"=== Execution ===\n{result.summary}\n"
        if result.result and result.result.returncode != 0:
            output_text += f"\nCommand failed with exit code {result.result.returncode}\n"
        
        if self.on_output_update:
            self.on_output_update(output_text)
        
        if self.on_status_update:
            status = "Execution complete" if result.result and result.result.returncode == 0 else "Execution failed"
            self.on_status_update(status)
        
        return result
    
    def propose_and_simulate(self, user_text: str) -> tuple[IntentType, Plan, SimulationResult]:
        """Full workflow: classify intent, build plan, and simulate.
        
        Args:
            user_text: User input text
            
        Returns:
            Tuple of (intent, plan, simulation_result)
        """
        intent = self.classify_intent(user_text)
        plan = self.plan_intent(intent)
        sim_result = self.simulate_plan(plan)
        return intent, plan, sim_result
    
    def explain(self, command: str) -> str:
        """Get explanation for a command using RAG.
        
        Args:
            command: Command to explain
            
        Returns:
            Explanation text
        """
        if self.on_status_update:
            self.on_status_update(f"Explaining: {command}")
        
        explanation = explain_command(command)
        
        if self.on_output_update:
            self.on_output_update(f"=== Explanation: {command} ===\n{explanation}\n")
        
        if self.on_status_update:
            self.on_status_update("Explanation ready")
        
        return explanation
    
    def get_history(self, limit: int = 20) -> list[OperationRecord]:
        """Get recent operation history.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of operation records
        """
        hist = get_history()
        return hist.get_recent(limit=limit)
    
    def replay_from_history(self, record: OperationRecord) -> None:
        """Replay a simulation from history.
        
        Args:
            record: History record to replay
        """
        if self.on_output_update:
            self.on_output_update(
                f"=== Replaying: {record.intent_type} ===\n"
                f"Command: {record.command}\n"
                f"Original status: {record.status}\n"
                f"Original output:\n{record.output_summary}\n"
            )
        
        if self.on_status_update:
            self.on_status_update(f"Replayed: {record.intent_type}")


__all__ = ["TinyLlamaPresenter"]
