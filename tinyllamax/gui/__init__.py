"""GTK 4 desktop GUI for TinyLlama-X.

Provides a graphical interface wrapping the existing tinyllamax core functionality:
- Intent planning and simulation
- Command execution with safety checks
- History viewing and replay
- Command explanation via RAG
"""

__all__ = ["gtk_app", "presenter", "services"]
