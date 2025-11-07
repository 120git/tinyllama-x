#!/usr/bin/env python3
"""
Distribution detection for Linux systems.
Parses /etc/os-release following freedesktop.org specification.
"""

from dataclasses import dataclass
from typing import Optional
import re
import subprocess


@dataclass
class DistroInfo:
    """Linux distribution information."""
    name: str  # e.g., "Ubuntu", "Fedora", "Arch Linux"
    version: str  # e.g., "22.04", "38", "rolling"
    id: str  # e.g., "ubuntu", "fedora", "arch"
    id_like: list[str]  # Parent distros, e.g., ["debian"]
    package_manager: str  # "apt", "dnf", "pacman", etc.
    
    def __str__(self):
        return f"{self.name} {self.version} ({self.package_manager})"


class DistroDetector:
    """Detects Linux distribution and package manager."""
    
    # Package manager detection rules
    PM_RULES = [
        # (package_manager, binary, id_patterns)
        ('apt', 'apt', ['ubuntu', 'debian', 'mint', 'pop', 'elementary']),
        ('dnf', 'dnf', ['fedora', 'rhel', 'centos', 'rocky', 'alma']),
        ('yum', 'yum', ['rhel', 'centos', 'oracle', 'scientific']),
        ('pacman', 'pacman', ['arch', 'manjaro', 'endeavouros']),
        ('zypper', 'zypper', ['opensuse', 'suse', 'sles']),
        ('emerge', 'emerge', ['gentoo']),
        ('apk', 'apk', ['alpine']),
    ]
    
    def detect(self) -> DistroInfo:
        """
        Detect current Linux distribution.
        Reads /etc/os-release (FreeDesktop standard).
        """
        os_info = self._parse_os_release()
        
        name = os_info.get('NAME', 'Unknown')
        version = os_info.get('VERSION_ID', os_info.get('VERSION', 'unknown'))
        distro_id = os_info.get('ID', 'unknown').lower()
        id_like_str = os_info.get('ID_LIKE', '')
        id_like = [x.strip() for x in id_like_str.split()] if id_like_str else []
        
        # Detect package manager
        pm = self._detect_package_manager(distro_id, id_like)
        
        return DistroInfo(
            name=name.strip('"'),
            version=version.strip('"'),
            id=distro_id,
            id_like=id_like,
            package_manager=pm
        )
    
    def _parse_os_release(self) -> dict:
        """Parse /etc/os-release file."""
        os_release_paths = ['/etc/os-release', '/usr/lib/os-release']
        
        for path in os_release_paths:
            try:
                with open(path, 'r') as f:
                    return self._parse_env_file(f.read())
            except FileNotFoundError:
                continue
            except PermissionError:
                continue
        
        # Fallback: try lsb_release command
        try:
            result = subprocess.run(
                ['lsb_release', '-a'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return self._parse_lsb_release(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {}
    
    def _parse_env_file(self, content: str) -> dict:
        """Parse shell-like environment file."""
        data = {}
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = re.match(r'^([A-Z_]+)=(.*)$', line)
            if match:
                key, value = match.groups()
                # Remove quotes
                value = value.strip('"').strip("'")
                data[key] = value
        
        return data
    
    def _parse_lsb_release(self, output: str) -> dict:
        """Parse lsb_release output."""
        data = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().replace(' ', '_').upper()
                data[key] = value.strip()
        
        return {
            'NAME': data.get('DISTRIBUTOR_ID', 'Unknown'),
            'VERSION_ID': data.get('RELEASE', 'unknown'),
            'ID': data.get('DISTRIBUTOR_ID', 'unknown').lower(),
        }
    
    def _detect_package_manager(self, distro_id: str, id_like: list[str]) -> str:
        """Detect package manager based on distro ID and hierarchy."""
        all_ids = [distro_id] + id_like
        
        # Try exact match first
        for pm, binary, patterns in self.PM_RULES:
            if distro_id in patterns:
                if self._command_exists(binary):
                    return pm
        
        # Try ID_LIKE hierarchy
        for pm, binary, patterns in self.PM_RULES:
            if any(id_val in patterns for id_val in all_ids):
                if self._command_exists(binary):
                    return pm
        
        # Fallback: check which PM binaries exist
        for pm, binary, _ in self.PM_RULES:
            if self._command_exists(binary):
                return pm
        
        return 'unknown'
    
    def _command_exists(self, cmd: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


# Singleton instance
_detector = DistroDetector()


def detect_distro() -> DistroInfo:
    """Convenience function to detect distribution."""
    return _detector.detect()


def get_install_command(package: str, distro: Optional[DistroInfo] = None) -> Optional[str]:
    """Get the install command for a package on current/specified distro."""
    if distro is None:
        distro = detect_distro()
    
    commands = {
        'apt': f'sudo apt install {package}',
        'dnf': f'sudo dnf install {package}',
        'yum': f'sudo yum install {package}',
        'pacman': f'sudo pacman -S {package}',
        'zypper': f'sudo zypper install {package}',
        'emerge': f'sudo emerge {package}',
        'apk': f'sudo apk add {package}',
    }
    
    return commands.get(distro.package_manager)


def get_update_command(distro: Optional[DistroInfo] = None) -> Optional[str]:
    """Get the system update command for current/specified distro."""
    if distro is None:
        distro = detect_distro()
    
    commands = {
        'apt': 'sudo apt update && sudo apt upgrade',
        'dnf': 'sudo dnf upgrade',
        'yum': 'sudo yum update',
        'pacman': 'sudo pacman -Syu',
        'zypper': 'sudo zypper update',
        'emerge': 'sudo emerge --sync && sudo emerge -uDN @world',
        'apk': 'sudo apk update && sudo apk upgrade',
    }
    
    return commands.get(distro.package_manager)
