#!/usr/bin/env bash
set -euo pipefail

# Build wheel and sdist to dist/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Building wheel and sdist..."
python -m build --outdir dist/

echo "Build complete. Artifacts in dist/:"
ls -lh dist/
