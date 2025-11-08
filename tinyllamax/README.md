# tinyllamax

Auxiliary Python CLI package for the TinyLlama-X ecosystem.

## Features
- Typer-based CLI (`tinyllamax` entrypoint)
- Simulation-first propose → simulate → confirm → run planning flow
- Distro detection + package manager adapters (apt, dnf, pacman, zypper, apk)
- RAG-lite command help via TLDR/man (safe fallbacks)
- Model-driven intent decision (Ollama or llama.cpp) with strict JSON output
- Pydantic config via env (`TINYLLAMAX_` prefix)

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

# Step 8: Model-driven intent decision (simulation by default; pass --run to execute)
tinyllamax chat "install htop" --backend ollama --model tinyllama:latest

## Developer tips

- Fake backend for demos/tests (no Ollama needed):
	- Simulation-only (JSON extracted from heuristics):
		```bash
		tinyllamax chat "install htop" --backend fake
		tinyllamax chat "search for curl" --backend fake
		tinyllamax chat "what does ls do?" --backend fake
		```
	- Force exact JSON for reproducible tests:
		```bash
		tinyllamax chat "ignored" --backend fake --fake-json '{"intent":"DetectDistro"}'
		```
	- Emit machine-readable output:
		```bash
		tinyllamax chat "install htop" --backend fake --json
		tinyllamax plan --search curl --json
		```
```

## Development
Run tests and static checks:
```bash
pytest
ruff check .
mypy tinyllamax
```

## License
MIT
