#!/usr/bin/env python3
"""Quick test suite for TinyLlama-X intelligence modules."""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from colorama import Fore, Style, init
init(autoreset=True)

def test_distro():
    """Test distribution detection."""
    print(f"\n{Fore.CYAN}=== Testing Distribution Detection ==={Style.RESET_ALL}")
    from distro import detect_distro, get_install_command, get_update_command
    
    distro = detect_distro()
    print(f"✓ Detected: {Fore.GREEN}{distro}{Style.RESET_ALL}")
    print(f"  ID: {distro.id}")
    print(f"  Package Manager: {distro.package_manager}")
    
    install_cmd = get_install_command('htop', distro)
    print(f"  Install command: {Fore.YELLOW}{install_cmd}{Style.RESET_ALL}")
    
    update_cmd = get_update_command(distro)
    print(f"  Update command: {Fore.YELLOW}{update_cmd}{Style.RESET_ALL}")

def test_intent():
    """Test intent classification."""
    print(f"\n{Fore.CYAN}=== Testing Intent Classification ==={Style.RESET_ALL}")
    from intent import classify_intent
    
    test_cases = [
        "install git",
        "what does rsync do?",
        "update my system",
        "remove firefox",
        "how do I copy files?",
        "what distro am I using?",
        "tell me about Linux",
    ]
    
    for query in test_cases:
        intent = classify_intent(query)
        confidence_color = Fore.GREEN if intent.confidence > 0.8 else Fore.YELLOW
        print(f"  '{query}'")
        print(f"    → {intent.type.value} {confidence_color}({intent.confidence:.0%}){Style.RESET_ALL}")
        if intent.entities:
            print(f"      Entities: {intent.entities}")

def test_pm_adapter():
    """Test package manager adapters."""
    print(f"\n{Fore.CYAN}=== Testing Package Manager Adapters ==={Style.RESET_ALL}")
    from distro import detect_distro
    from pm_adapter import get_adapter
    
    distro = detect_distro()
    adapter = get_adapter(distro.package_manager, dry_run=True)
    
    if adapter:
        print(f"✓ Got adapter for {Fore.GREEN}{distro.package_manager}{Style.RESET_ALL}")
        print(f"  Testing dry-run search...")
        result = adapter.search('htop')
        if result.success:
            print(f"  {Fore.GREEN}✓ Search works{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ Search failed (may be expected){Style.RESET_ALL}")
    else:
        print(f"  {Fore.RED}✗ No adapter available{Style.RESET_ALL}")

def test_rag():
    """Test command help (RAG-lite)."""
    print(f"\n{Fore.CYAN}=== Testing Command Help (RAG) ==={Style.RESET_ALL}")
    from rag import explain_command
    
    commands = ['ls', 'rsync', 'rm']
    
    for cmd in commands:
        help_info = explain_command(cmd)
        if help_info:
            print(f"  {Fore.GREEN}✓ {cmd}{Style.RESET_ALL}: {help_info.description[:60]}...")
            if help_info.safety_warning:
                print(f"    {Fore.RED}{help_info.safety_warning}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ {cmd}: No help found{Style.RESET_ALL}")

def test_executor():
    """Test safe executor (dry-run only)."""
    print(f"\n{Fore.CYAN}=== Testing Safe Executor ==={Style.RESET_ALL}")
    from executor import SafeExecutor, RiskLevel
    
    executor = SafeExecutor(interactive=False)
    
    test_commands = [
        ('ls -la', RiskLevel.LOW),
        ('sudo apt install htop', RiskLevel.MEDIUM),
        ('rm -rf /', RiskLevel.HIGH),
    ]
    
    for cmd, expected_risk in test_commands:
        plan = executor.plan(cmd)
        risk_color = {
            RiskLevel.LOW: Fore.GREEN,
            RiskLevel.MEDIUM: Fore.YELLOW,
            RiskLevel.HIGH: Fore.RED,
        }[plan.risk_level]
        
        match = "✓" if plan.risk_level == expected_risk else "✗"
        print(f"  {match} '{cmd}'")
        print(f"    → Risk: {risk_color}{plan.risk_level.value}{Style.RESET_ALL}")

def test_history():
    """Test operation history."""
    print(f"\n{Fore.CYAN}=== Testing Operation History ==={Style.RESET_ALL}")
    from history import log_operation, get_recent_operations
    
    # Log a test operation
    op_id = log_operation(
        intent_type='test',
        command='echo test',
        status='success',
        output_summary='test output'
    )
    print(f"  ✓ Logged operation #{op_id}")
    
    # Retrieve recent
    recent = get_recent_operations(limit=5)
    print(f"  ✓ Retrieved {len(recent)} recent operations")
    
    if recent:
        latest = recent[0]
        print(f"    Latest: {latest.intent_type} - {latest.command[:30]}... [{latest.status}]")

def main():
    """Run all tests."""
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}TinyLlama-X Intelligence Test Suite{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    try:
        test_distro()
        test_intent()
        test_pm_adapter()
        test_rag()
        test_executor()
        test_history()
        
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}All tests completed!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"\n{Fore.RED}Test failed: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
