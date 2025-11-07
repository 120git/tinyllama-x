#!/usr/bin/env python3
"""
RAG-lite command help using tldr pages and man summaries.
Provides quick examples and safety warnings for common commands.
"""

from dataclasses import dataclass
from typing import Optional
import subprocess
import os
import json
import urllib.request
import urllib.error
from pathlib import Path


@dataclass
class CommandHelp:
    """Command help information."""
    command: str
    description: str
    examples: list[str]
    safety_warning: Optional[str] = None
    source: str = "unknown"  # "tldr", "man", "builtin"


class CommandHelpProvider:
    """Provides command help from tldr and man pages."""
    
    # Builtin safety warnings for dangerous commands
    SAFETY_WARNINGS = {
        'rm': '⚠️  Destructive! Use -i for interactive, avoid -rf without careful review.',
        'dd': '⚠️  DANGEROUS! Can overwrite entire disks. Double-check if= and of= parameters.',
        'mkfs': '⚠️  Formats/erases filesystems. Verify device path before executing.',
        'chmod': '⚠️  Can break file permissions. Avoid 777; use specific user/group perms.',
        'chown': '⚠️  Changes ownership. May lock you out of files if used incorrectly.',
        'sudo': '⚠️  Grants root privileges. Verify command safety before executing.',
        'systemctl': '⚠️  Controls system services. stop/disable can break critical services.',
        'fdisk': '⚠️  Partition editor. Can destroy data if partitions are modified.',
        'parted': '⚠️  Partition editor. Mistakes can result in data loss.',
        'reboot': '⚠️  Immediately reboots system. Save work first.',
        'shutdown': '⚠️  Powers down system. Save work and notify users.',
        'kill': 'Terminates processes. Use -9 (SIGKILL) only as last resort.',
        'pkill': 'Kills processes by name. May affect multiple processes.',
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize command help provider.
        
        Args:
            cache_dir: Directory to cache tldr pages (default: ~/.cache/tinyllama-x/tldr)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.cache/tinyllama-x/tldr')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_help(self, command: str) -> Optional[CommandHelp]:
        """
        Get help for a command.
        Tries tldr first, falls back to man page summary.
        """
        # Try tldr first
        tldr_help = self._get_tldr(command)
        if tldr_help:
            return tldr_help
        
        # Fallback to man page
        man_help = self._get_man_summary(command)
        if man_help:
            return man_help
        
        return None
    
    def _get_tldr(self, command: str) -> Optional[CommandHelp]:
        """Get help from tldr pages."""
        # Try cache first
        cached = self._get_cached_tldr(command)
        if cached:
            return cached
        
        # Fetch from tldr-pages repository
        return self._fetch_tldr(command)
    
    def _get_cached_tldr(self, command: str) -> Optional[CommandHelp]:
        """Get tldr page from local cache."""
        platforms = ['linux', 'common']
        
        for platform in platforms:
            cache_file = self.cache_dir / platform / f'{command}.json'
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        return self._parse_tldr_json(data)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return None
    
    def _fetch_tldr(self, command: str) -> Optional[CommandHelp]:
        """Fetch tldr page from GitHub."""
        platforms = ['linux', 'common']
        base_url = 'https://raw.githubusercontent.com/tldr-pages/tldr/main/pages'
        
        for platform in platforms:
            url = f'{base_url}/{platform}/{command}.md'
            
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    content = response.read().decode('utf-8')
                    help_obj = self._parse_tldr_markdown(command, content)
                    
                    # Cache it
                    cache_file = self.cache_dir / platform / f'{command}.json'
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(cache_file, 'w') as f:
                        json.dump({
                            'name': command,
                            'description': help_obj.description,
                            'examples': [{'description': ex} for ex in help_obj.examples]
                        }, f)
                    
                    return help_obj
            
            except (urllib.error.URLError, urllib.error.HTTPError):
                continue
        
        return None
    
    def _parse_tldr_markdown(self, command: str, content: str) -> CommandHelp:
        """Parse tldr markdown format."""
        lines = content.strip().split('\n')
        
        # First line after # is description
        description = ""
        examples = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('# '):
                continue  # Skip title
            elif line.startswith('>'):
                description = line.lstrip('> ').strip()
            elif line.startswith('-'):
                # Example description
                examples.append(line.lstrip('- ').strip())
            elif line.startswith('`') and line.endswith('`'):
                # Example command (attach to last example)
                if examples:
                    examples[-1] += f"\n  {line.strip('`')}"
        
        return CommandHelp(
            command=command,
            description=description,
            examples=examples,
            safety_warning=self.SAFETY_WARNINGS.get(command),
            source='tldr'
        )
    
    def _parse_tldr_json(self, data: dict) -> CommandHelp:
        """Parse tldr JSON format."""
        examples = []
        for ex in data.get('examples', []):
            desc = ex.get('description', '')
            cmd = ex.get('command', '')
            if desc:
                examples.append(f"{desc}\n  {cmd}" if cmd else desc)
        
        return CommandHelp(
            command=data.get('name', 'unknown'),
            description=data.get('description', ''),
            examples=examples,
            safety_warning=self.SAFETY_WARNINGS.get(data.get('name')),
            source='tldr'
        )
    
    def _get_man_summary(self, command: str) -> Optional[CommandHelp]:
        """Get summary from man page."""
        try:
            # Get NAME section from man page
            result = subprocess.run(
                ['man', command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            # Extract NAME section (simple heuristic)
            lines = result.stdout.split('\n')
            description = ""
            
            in_name_section = False
            for line in lines:
                if 'NAME' in line:
                    in_name_section = True
                    continue
                
                if in_name_section:
                    line = line.strip()
                    if line and not line.isupper():
                        # Extract description after command name
                        if '-' in line:
                            description = line.split('-', 1)[1].strip()
                        else:
                            description = line
                        break
            
            if description:
                return CommandHelp(
                    command=command,
                    description=description,
                    examples=[],
                    safety_warning=self.SAFETY_WARNINGS.get(command),
                    source='man'
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None


# Singleton instance
_provider = CommandHelpProvider()


def explain_command(command: str) -> Optional[CommandHelp]:
    """Convenience function to get command help."""
    return _provider.get_help(command)
