"""Prompt templates for intent decision.

Contains a system prompt enforcing STRICT JSON single-object output and a few
few-shot examples to guide the model.
"""
from __future__ import annotations

SYSTEM_PROMPT = (
    "You are an intent classification engine for a Linux assistant. "
    "Output EXACTLY ONE JSON object matching one of these intents: "
    "DetectDistro | SearchPackage | InstallPackage | RemovePackage | "
    "UpdateSystem | UpgradeSystem | ExplainCommand | TroubleshootError. "
    "NO prose, NO extra lines, NO markdown fences. Just JSON."
)

FEW_SHOTS = [
    # (user, expected JSON)
    ("install htop", {"intent": "InstallPackage", "package": "htop"}),
    ("remove neovim", {"intent": "RemovePackage", "package": "neovim"}),
    ("what does ls do?", {"intent": "ExplainCommand", "command": "ls"}),
    ("update my system", {"intent": "UpdateSystem"}),
    ("upgrade everything", {"intent": "UpgradeSystem"}),
    ("search for curl", {"intent": "SearchPackage", "query": "curl"}),
    ("what distro am i on", {"intent": "DetectDistro"}),
]


def build_system_prompt() -> str:
    """Compose the full system prompt including few-shot examples."""
    lines = [SYSTEM_PROMPT, "Examples:"]
    for user, js in FEW_SHOTS:
        lines.append(f"User: {user}\nJSON: {js}")
    return "\n\n".join(lines)

__all__ = ["build_system_prompt"]
