#!/usr/bin/env python3
"""
Package manager adapters with dry-run support.
Provides unified interface for apt, dnf, pacman, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
import subprocess
import shlex


@dataclass
class CommandResult:
    """Result of a package manager command."""
    success: bool
    command: str
    stdout: str
    stderr: str
    returncode: int
    dry_run: bool = False


class PackageManagerAdapter(ABC):
    """Base adapter for package managers."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
    
    @abstractmethod
    def install(self, packages: List[str]) -> CommandResult:
        """Install one or more packages."""
        pass
    
    @abstractmethod
    def remove(self, packages: List[str]) -> CommandResult:
        """Remove one or more packages."""
        pass
    
    @abstractmethod
    def update(self) -> CommandResult:
        """Update package lists and upgrade installed packages."""
        pass
    
    @abstractmethod
    def search(self, query: str) -> CommandResult:
        """Search for packages matching query."""
        pass
    
    def _execute(self, cmd: List[str], simulate_flag: Optional[str] = None) -> CommandResult:
        """
        Execute command with optional dry-run/simulation.
        
        Args:
            cmd: Command to execute as list
            simulate_flag: Flag to add for dry-run (e.g., '--dry-run', '-s')
        """
        if self.dry_run and simulate_flag:
            cmd = cmd + [simulate_flag]
        
        cmd_str = ' '.join(shlex.quote(arg) for arg in cmd)
        
        if self.dry_run and not simulate_flag:
            # No native dry-run support; just preview
            return CommandResult(
                success=True,
                command=cmd_str,
                stdout=f"[DRY RUN] Would execute: {cmd_str}",
                stderr="",
                returncode=0,
                dry_run=True
            )
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return CommandResult(
                success=result.returncode == 0,
                command=cmd_str,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                dry_run=self.dry_run
            )
        
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                command=cmd_str,
                stdout="",
                stderr="Command timed out after 5 minutes",
                returncode=-1,
                dry_run=self.dry_run
            )
        except Exception as e:
            return CommandResult(
                success=False,
                command=cmd_str,
                stdout="",
                stderr=f"Error executing command: {e}",
                returncode=-1,
                dry_run=self.dry_run
            )


class AptAdapter(PackageManagerAdapter):
    """Adapter for APT (Debian, Ubuntu)."""
    
    def install(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'apt', 'install', '-y'] + packages
        return self._execute(cmd, simulate_flag='--dry-run' if self.dry_run else None)
    
    def remove(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'apt', 'remove', '-y'] + packages
        return self._execute(cmd, simulate_flag='--dry-run' if self.dry_run else None)
    
    def update(self) -> CommandResult:
        # APT doesn't have good dry-run for update+upgrade combo
        if self.dry_run:
            return CommandResult(
                success=True,
                command='sudo apt update && sudo apt upgrade -y',
                stdout='[DRY RUN] Would update package lists and upgrade all packages',
                stderr='',
                returncode=0,
                dry_run=True
            )
        
        # Update package lists first
        update_result = self._execute(['sudo', 'apt', 'update'])
        if not update_result.success:
            return update_result
        
        # Then upgrade
        return self._execute(['sudo', 'apt', 'upgrade', '-y'])
    
    def search(self, query: str) -> CommandResult:
        return self._execute(['apt', 'search', query])


class DnfAdapter(PackageManagerAdapter):
    """Adapter for DNF (Fedora, RHEL 8+)."""
    
    def install(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'dnf', 'install', '-y'] + packages
        # DNF has --assumeno for dry-run simulation
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def remove(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'dnf', 'remove', '-y'] + packages
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def update(self) -> CommandResult:
        cmd = ['sudo', 'dnf', 'upgrade', '-y']
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def search(self, query: str) -> CommandResult:
        return self._execute(['dnf', 'search', query])


class PacmanAdapter(PackageManagerAdapter):
    """Adapter for Pacman (Arch Linux, Manjaro)."""
    
    def install(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
        # Pacman doesn't have native dry-run, use preview
        if self.dry_run:
            # Remove noconfirm to let user see what would be installed
            cmd.remove('--noconfirm')
            cmd.append('--print')
        return self._execute(cmd)
    
    def remove(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'pacman', '-R', '--noconfirm'] + packages
        if self.dry_run:
            cmd.remove('--noconfirm')
            cmd.append('--print')
        return self._execute(cmd)
    
    def update(self) -> CommandResult:
        cmd = ['sudo', 'pacman', '-Syu', '--noconfirm']
        if self.dry_run:
            # Show what would be updated
            return self._execute(['pacman', '-Qu'])  # List upgradeable
        return self._execute(cmd)
    
    def search(self, query: str) -> CommandResult:
        return self._execute(['pacman', '-Ss', query])


class YumAdapter(PackageManagerAdapter):
    """Adapter for YUM (RHEL/CentOS 7 and earlier)."""
    
    def install(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'yum', 'install', '-y'] + packages
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def remove(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'yum', 'remove', '-y'] + packages
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def update(self) -> CommandResult:
        cmd = ['sudo', 'yum', 'update', '-y']
        if self.dry_run:
            cmd.remove('-y')
            cmd.append('--assumeno')
        return self._execute(cmd)
    
    def search(self, query: str) -> CommandResult:
        return self._execute(['yum', 'search', query])


class ZypperAdapter(PackageManagerAdapter):
    """Adapter for Zypper (openSUSE)."""
    
    def install(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'zypper', 'install', '-y'] + packages
        if self.dry_run:
            cmd.insert(2, '--dry-run')
        return self._execute(cmd)
    
    def remove(self, packages: List[str]) -> CommandResult:
        cmd = ['sudo', 'zypper', 'remove', '-y'] + packages
        if self.dry_run:
            cmd.insert(2, '--dry-run')
        return self._execute(cmd)
    
    def update(self) -> CommandResult:
        cmd = ['sudo', 'zypper', 'update', '-y']
        if self.dry_run:
            cmd.insert(2, '--dry-run')
        return self._execute(cmd)
    
    def search(self, query: str) -> CommandResult:
        return self._execute(['zypper', 'search', query])


def get_adapter(pm_name: str, dry_run: bool = False) -> Optional[PackageManagerAdapter]:
    """Factory function to get appropriate adapter."""
    adapters = {
        'apt': AptAdapter,
        'dnf': DnfAdapter,
        'yum': YumAdapter,
        'pacman': PacmanAdapter,
        'zypper': ZypperAdapter,
    }
    
    adapter_class = adapters.get(pm_name)
    if adapter_class:
        return adapter_class(dry_run=dry_run)
    return None
