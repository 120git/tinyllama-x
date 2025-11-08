# tinyllamax

Auxiliary Python CLI package for the TinyLlama-X ecosystem.

## Features
- Typer-based CLI (`tinyllamax` entrypoint)
- Simulation-first propose → simulate → confirm → run planning flow
- Distro detection + package manager adapters (apt, dnf, pacman, zypper, apk)
- RAG-lite command help via TLDR/man (safe fallbacks)
- Model-driven intent decision (Ollama or llama.cpp) with strict JSON output
- Pydantic config via env (`TINYLLAMAX_` prefix)
- Session history tracking with SQLite database (audit trail, troubleshooting)

## Installation (editable)
```bash
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
```

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
