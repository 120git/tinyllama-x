# tinyllamax

Auxiliary Python CLI package for the TinyLlama-X ecosystem.

## Features
- Typer-based CLI (`tinyllamax` entrypoint)
- Pydantic configuration model loading from environment (`TINYLLAMAX_` prefix)
- Placeholder domain models for package actions and command explanation

## Installation (editable)
```bash
pip install -e .
```

## Usage
```bash
tinyllamax --help
tinyllamax settings
tinyllamax explain "ls -la" --detail 2
tinyllamax pkg install --packages htop,git
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
