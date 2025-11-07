"""Intent models and parsing utilities for tinyllamax.

Defines structured Pydantic models representing user intents routed through the CLI.
Each intent has a distinct schema to allow downstream validation and execution planning.
"""
from __future__ import annotations

from typing import Any, Dict, Type, Union
from pydantic import BaseModel, Field, ValidationError

# --------------------
# Intent Model Classes
# --------------------

class DetectDistro(BaseModel):
    intent: str = Field(default="DetectDistro", frozen=True)

class SearchPackage(BaseModel):
    intent: str = Field(default="SearchPackage", frozen=True)
    query: str = Field(min_length=1, description="Search term for package lookup")

class InstallPackage(BaseModel):
    intent: str = Field(default="InstallPackage", frozen=True)
    package: str = Field(min_length=1, description="Single package name to install")
    assume_yes: bool = Field(default=False, description="Proceed without interactive confirmation")

class RemovePackage(BaseModel):
    intent: str = Field(default="RemovePackage", frozen=True)
    package: str = Field(min_length=1, description="Single package name to remove")
    assume_yes: bool = Field(default=False, description="Proceed without interactive confirmation")

class UpdateSystem(BaseModel):
    intent: str = Field(default="UpdateSystem", frozen=True)

class UpgradeSystem(BaseModel):
    intent: str = Field(default="UpgradeSystem", frozen=True)

class ExplainCommand(BaseModel):
    intent: str = Field(default="ExplainCommand", frozen=True)
    command: str = Field(min_length=1, description="Shell command to explain")

class TroubleshootError(BaseModel):
    intent: str = Field(default="TroubleshootError", frozen=True)
    error_text: str = Field(min_length=1, description="Raw error text to analyze")

# Union type for convenience
IntentType = Union[
    DetectDistro,
    SearchPackage,
    InstallPackage,
    RemovePackage,
    UpdateSystem,
    UpgradeSystem,
    ExplainCommand,
    TroubleshootError,
]

# Map intent names to model classes for dynamic parsing
_INTENT_MODEL_MAP: Dict[str, Type[BaseModel]] = {
    "DetectDistro": DetectDistro,
    "SearchPackage": SearchPackage,
    "InstallPackage": InstallPackage,
    "RemovePackage": RemovePackage,
    "UpdateSystem": UpdateSystem,
    "UpgradeSystem": UpgradeSystem,
    "ExplainCommand": ExplainCommand,
    "TroubleshootError": TroubleshootError,
}

class IntentParseError(ValueError):
    """Raised when intent parsing fails."""
    def __init__(self, message: str, details: Any | None = None):
        super().__init__(message)
        self.details = details

def parse_intent(obj: Dict[str, Any]) -> IntentType:
    """Parse a dictionary into the appropriate intent model.

    Expected format: {"intent": "Name", ...fields}

    Returns:
        IntentType instance corresponding to the 'intent' field.

    Raises:
        IntentParseError: if 'intent' missing, unknown, or validation fails.
    """
    if not isinstance(obj, dict):
        raise IntentParseError("Input must be a dict", details={"got_type": type(obj).__name__})

    intent_name = obj.get("intent")
    if not intent_name:
        raise IntentParseError("Missing 'intent' field", details=obj)

    model_cls = _INTENT_MODEL_MAP.get(str(intent_name))
    if model_cls is None:
        raise IntentParseError(
            f"Unknown intent '{intent_name}'",
            details={"allowed": sorted(_INTENT_MODEL_MAP.keys())}
        )

    try:
        parsed = model_cls(**obj)
        assert isinstance(parsed, (DetectDistro, SearchPackage, InstallPackage, RemovePackage, UpdateSystem, UpgradeSystem, ExplainCommand, TroubleshootError))
        return parsed
    except ValidationError as ve:
        raise IntentParseError(
            f"Validation failed for intent '{intent_name}'",
            details=ve.errors()
        ) from ve

__all__ = [
    "DetectDistro",
    "SearchPackage",
    "InstallPackage",
    "RemovePackage",
    "UpdateSystem",
    "UpgradeSystem",
    "ExplainCommand",
    "TroubleshootError",
    "IntentType",
    "parse_intent",
    "IntentParseError",
]
