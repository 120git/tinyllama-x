"""TinyLlama-X intelligent terminal assistant library."""

from .intent import classify_intent, Intent, IntentType
from .distro import detect_distro, DistroInfo, get_install_command, get_update_command
from .pm_adapter import get_adapter, PackageManagerAdapter, CommandResult
from .rag import explain_command, CommandHelp
from .executor import SafeExecutor, ExecutionPlan, ExecutionResult, RiskLevel
from .history import (
    log_operation, 
    get_recent_operations, 
    find_similar_failures,
    OperationRecord
)

__all__ = [
    # Intent detection
    'classify_intent', 'Intent', 'IntentType',
    
    # Distribution detection
    'detect_distro', 'DistroInfo', 'get_install_command', 'get_update_command',
    
    # Package manager adapters
    'get_adapter', 'PackageManagerAdapter', 'CommandResult',
    
    # Command help (RAG-lite)
    'explain_command', 'CommandHelp',
    
    # Safe execution
    'SafeExecutor', 'ExecutionPlan', 'ExecutionResult', 'RiskLevel',
    
    # History tracking
    'log_operation', 'get_recent_operations', 'find_similar_failures', 'OperationRecord',
]
