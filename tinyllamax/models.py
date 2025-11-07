"""Domain models for tinyllamax (placeholders)."""
from pydantic import BaseModel, Field


class PackageAction(BaseModel):
    action: str = Field(pattern=r"^(install|remove|update|search)$")
    packages: list[str] = Field(default_factory=list)

class CommandExplain(BaseModel):
    command: str
    detail_level: int = 1
