"""Configuration models for tinyllamax using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings loaded from env vars or .env file.

    Environment variable prefix: TINYLLAMAX_
    """
    model_path: str | None = Field(default=None, description="Path to GGUF model")
    venv_path: str | None = Field(default=None, description="Path to Python virtual environment")
    verbose: bool = Field(default=False, description="Enable verbose logging")

    # Pydantic SettingsConfigDict fields
    model_config = {
        "env_prefix": "TINYLLAMAX_",
        "case_sensitive": False,
        "frozen": True,
    }
