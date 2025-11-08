# tinyllamax

Auxiliary Python CLI package for the TinyLlama-X ecosystem.

## Features
- Typer-based CLI (`tinyllamax` entrypoint)
- **GTK 4 Desktop GUI** for graphical interaction
- Simulation-first propose → simulate → confirm → run planning flow
- Distro detection + package manager adapters (apt, dnf, pacman, zypper, apk)
- RAG-lite command help via TLDR/man (safe fallbacks)
- Model-driven intent decision (Ollama or llama.cpp) with strict JSON output
- Pydantic config via env (`TINYLLAMAX_` prefix)
- Session history tracking with SQLite database (audit trail, troubleshooting)

## Installation

### Basic Installation
```bash
pip install -e .
```

### With GUI Support
```bash
pip install -e .[gui]
# Or on Ubuntu/Debian:
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
pip install -e .
```

## Usage
```bash
# General
tinyllamax --help
tinyllamax settings

# Plan an action (simulate first, optional real run with --real)
tinyllamax plan --install htop
tinyllamax plan --remove neovim
tinyllamax plan --search curl
tinyllamax plan --update
tinyllamax plan --upgrade
tinyllamax plan --explain "ls -la"

# Feed raw JSON intent for debugging
tinyllamax debug-intent --json '{"intent":"InstallPackage","package":"htop"}'

# Model-driven intent decision (simulation by default; pass --run to execute)
tinyllamax chat "install htop" --backend ollama --model tinyllama:latest

# View command history
tinyllamax history --limit 20
tinyllamax history --intent InstallPackage
tinyllamax history --status failed
tinyllamax history --stats

# Launch GTK Desktop GUI
tinyllamax gui
```

## Desktop GUI
The GTK 4 desktop interface provides:
- Visual command input with intent classification
- Propose/Simulate workflow with output console
- Real command execution with confirmation dialogs
- Command explanation via RAG
- Operation history viewer with replay capability
- Backend selection (Ollama, Llama.cpp, or Fake for testing)
- Non-blocking operations with cancellation support

## Session History
All operations (simulations and executions) are logged to `~/.local/share/tinyllamax/history.sqlite`. This provides:
- Audit trail of all commands executed
- Troubleshooting aid for failed operations
- Success rate statistics by intent type
- Similar failure pattern detection

## Development
Run tests and static checks:
```bash
pytest
ruff check .
mypy tinyllamax
```

## License
MIT
