#!/usr/bin/env python3
"""
Safe command execution engine with propose→confirm→simulate→run workflow.
Includes risk assessment and undo hints.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
import subprocess
import shlex
from colorama import Fore, Style


class RiskLevel(Enum):
    """Command risk levels."""
    LOW = "low"          # Read-only operations
    MEDIUM = "medium"    # Reversible modifications
    HIGH = "high"        # Destructive/system-wide changes


@dataclass
class ExecutionPlan:
    """Planned command execution."""
    command: str
    description: str
    risk_level: RiskLevel
    undo_hint: Optional[str] = None
    dry_run_available: bool = False
    requires_sudo: bool = False


@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    command: str
    stdout: str
    stderr: str
    returncode: int
    was_dry_run: bool = False


class SafeExecutor:
    """
    Safe command executor with confirmation gates.
    Implements: propose → confirm → simulate → run workflow.
    """
    
    # Risk patterns for common commands
    RISK_PATTERNS = {
        RiskLevel.HIGH: [
            'rm -rf', 'dd', 'mkfs', 'fdisk', 'parted', 'reboot', 'shutdown',
            'systemctl stop', 'systemctl disable', 'kill -9', 'pkill -9',
        ],
        RiskLevel.MEDIUM: [
            'rm ', 'mv', 'chmod', 'chown', 'apt install', 'dnf install',
            'pacman -S', 'systemctl restart', 'kill ', 'pkill ',
        ],
        RiskLevel.LOW: [
            'ls', 'cat', 'grep', 'find', 'which', 'apt search', 'man',
            'systemctl status', 'ps', 'top', 'df', 'du',
        ],
    }
    
    # Undo hints for common operations
    UNDO_HINTS = {
        'apt install': 'Undo: sudo apt remove <package>',
        'dnf install': 'Undo: sudo dnf remove <package>',
        'pacman -S': 'Undo: sudo pacman -R <package>',
        'systemctl stop': 'Undo: sudo systemctl start <service>',
        'systemctl disable': 'Undo: sudo systemctl enable <service>',
        'chmod': 'Undo: chmod with original permissions',
        'chown': 'Undo: chown with original owner:group',
    }
    
    def __init__(self, interactive: bool = True, auto_confirm_low_risk: bool = False):
        """
        Initialize executor.
        
        Args:
            interactive: If True, prompt for confirmation
            auto_confirm_low_risk: If True, auto-confirm LOW risk commands
        """
        self.interactive = interactive
        self.auto_confirm_low_risk = auto_confirm_low_risk
    
    def plan(self, command: str, description: str = "") -> ExecutionPlan:
        """
        Create an execution plan for a command.
        Assesses risk and provides undo hints.
        """
        risk = self._assess_risk(command)
        undo_hint = self._get_undo_hint(command)
        requires_sudo = 'sudo' in command or command.startswith('/usr')
        dry_run_available = self._supports_dry_run(command)
        
        return ExecutionPlan(
            command=command,
            description=description or f"Execute: {command}",
            risk_level=risk,
            undo_hint=undo_hint,
            dry_run_available=dry_run_available,
            requires_sudo=requires_sudo
        )
    
    def execute(self, plan: ExecutionPlan, 
                confirm_callback: Optional[Callable[[ExecutionPlan], bool]] = None) -> ExecutionResult:
        """
        Execute a planned command with safety checks.
        
        Args:
            plan: Execution plan
            confirm_callback: Optional callback for custom confirmation logic
        
        Returns:
            ExecutionResult with command output
        """
        # 1. PROPOSE: Show what will be executed
        self._display_plan(plan)
        
        # 2. CONFIRM: Get user approval
        if self.interactive:
            if confirm_callback:
                if not confirm_callback(plan):
                    return self._cancelled_result(plan)
            else:
                if not self._default_confirm(plan):
                    return self._cancelled_result(plan)
        
        # 3. SIMULATE: Run dry-run if available
        if plan.dry_run_available and plan.risk_level != RiskLevel.LOW:
            print(f"\n{Fore.YELLOW}Running simulation...{Style.RESET_ALL}")
            dry_result = self._execute_command(plan.command, dry_run=True)
            self._display_result(dry_result)
            
            if self.interactive:
                response = input(f"\n{Fore.CYAN}Proceed with actual execution? [y/N]: {Style.RESET_ALL}").lower()
                if response != 'y':
                    return self._cancelled_result(plan)
        
        # 4. RUN: Execute the command
        print(f"\n{Fore.GREEN}Executing...{Style.RESET_ALL}")
        result = self._execute_command(plan.command, dry_run=False)
        self._display_result(result)
        
        return result
    
    def _assess_risk(self, command: str) -> RiskLevel:
        """Assess risk level of a command."""
        cmd_lower = command.lower()
        
        # Check HIGH risk patterns
        for pattern in self.RISK_PATTERNS[RiskLevel.HIGH]:
            if pattern in cmd_lower:
                return RiskLevel.HIGH
        
        # Check MEDIUM risk patterns
        for pattern in self.RISK_PATTERNS[RiskLevel.MEDIUM]:
            if pattern in cmd_lower:
                return RiskLevel.MEDIUM
        
        # Check LOW risk patterns
        for pattern in self.RISK_PATTERNS[RiskLevel.LOW]:
            if pattern in cmd_lower:
                return RiskLevel.LOW
        
        # Default to MEDIUM for unknown commands
        return RiskLevel.MEDIUM
    
    def _get_undo_hint(self, command: str) -> Optional[str]:
        """Get undo hint for a command."""
        for pattern, hint in self.UNDO_HINTS.items():
            if pattern in command:
                return hint
        return None
    
    def _supports_dry_run(self, command: str) -> bool:
        """Check if command supports dry-run."""
        dry_run_commands = ['apt', 'dnf', 'zypper', 'rsync']
        return any(cmd in command for cmd in dry_run_commands)
    
    def _display_plan(self, plan: ExecutionPlan):
        """Display execution plan with color-coded risk."""
        risk_colors = {
            RiskLevel.LOW: Fore.GREEN,
            RiskLevel.MEDIUM: Fore.YELLOW,
            RiskLevel.HIGH: Fore.RED,
        }
        
        color = risk_colors[plan.risk_level]
        
        print(f"\n{'='*60}")
        print(f"{color}EXECUTION PLAN{Style.RESET_ALL}")
        print(f"{'='*60}")
        print(f"Description: {plan.description}")
        print(f"Command:     {Fore.CYAN}{plan.command}{Style.RESET_ALL}")
        print(f"Risk Level:  {color}{plan.risk_level.value.upper()}{Style.RESET_ALL}")
        
        if plan.undo_hint:
            print(f"Undo Hint:   {Fore.BLUE}{plan.undo_hint}{Style.RESET_ALL}")
        
        if plan.requires_sudo:
            print(f"{Fore.YELLOW}⚠️  Requires root privileges{Style.RESET_ALL}")
        
        print(f"{'='*60}\n")
    
    def _default_confirm(self, plan: ExecutionPlan) -> bool:
        """Default confirmation prompt."""
        # Auto-confirm low-risk if configured
        if plan.risk_level == RiskLevel.LOW and self.auto_confirm_low_risk:
            return True
        
        risk_prompts = {
            RiskLevel.LOW: f"{Fore.GREEN}Execute this command? [Y/n]: {Style.RESET_ALL}",
            RiskLevel.MEDIUM: f"{Fore.YELLOW}Proceed with this operation? [y/N]: {Style.RESET_ALL}",
            RiskLevel.HIGH: f"{Fore.RED}⚠️  HIGH RISK! Type 'yes' to confirm: {Style.RESET_ALL}",
        }
        
        prompt = risk_prompts[plan.risk_level]
        response = input(prompt).lower().strip()
        
        if plan.risk_level == RiskLevel.HIGH:
            return response == 'yes'
        elif plan.risk_level == RiskLevel.MEDIUM:
            return response == 'y'
        else:  # LOW
            return response != 'n'
    
    def _execute_command(self, command: str, dry_run: bool = False) -> ExecutionResult:
        """Execute a shell command."""
        try:
            # Add dry-run flag if supported
            if dry_run:
                if 'apt' in command:
                    command += ' --dry-run'
                elif 'dnf' in command or 'yum' in command:
                    command = command.replace('-y', '--assumeno')
                elif 'zypper' in command:
                    command = command.replace('install', 'install --dry-run')
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return ExecutionResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                was_dry_run=dry_run
            )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr="Command timed out",
                returncode=-1,
                was_dry_run=dry_run
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr=f"Error: {e}",
                returncode=-1,
                was_dry_run=dry_run
            )
    
    def _display_result(self, result: ExecutionResult):
        """Display execution result."""
        if result.was_dry_run:
            print(f"{Fore.YELLOW}[DRY RUN RESULT]{Style.RESET_ALL}")
        
        if result.success:
            print(f"{Fore.GREEN}✓ Command completed successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Command failed (exit code: {result.returncode}){Style.RESET_ALL}")
        
        if result.stdout:
            print(f"\nOutput:\n{result.stdout}")
        
        if result.stderr:
            print(f"\n{Fore.YELLOW}Errors/Warnings:\n{result.stderr}{Style.RESET_ALL}")
    
    def _cancelled_result(self, plan: ExecutionPlan) -> ExecutionResult:
        """Create a cancelled execution result."""
        return ExecutionResult(
            success=False,
            command=plan.command,
            stdout="",
            stderr="Execution cancelled by user",
            returncode=-2
        )
