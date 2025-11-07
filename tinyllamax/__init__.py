"""tinyllamax: High-level CLI utilities for TinyLlama-X ecosystem.

Provides a Typer-powered command-line interface and Pydantic-based configuration models.
"""
from .config import AppSettings

__all__ = ["AppSettings"]
__version__ = "0.1.0"