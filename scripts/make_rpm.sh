#!/usr/bin/env bash
set -euo pipefail

# Build .rpm package using fpm

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION="${VERSION:-0.1.0}"
OUT_DIR="${OUT_DIR:-$PROJECT_ROOT/out}"

cd "$PROJECT_ROOT"

# Ensure wheel is built
if [ ! -f "dist/tinyllamax-${VERSION}-py3-none-any.whl" ]; then
    echo "Building wheel first..."
    bash scripts/build_wheel.sh
fi

# Check for fpm
if ! command -v fpm &> /dev/null; then
    echo "fpm not found. Installing via gem..."
    gem install --user-install fpm
    export PATH="$HOME/.local/share/gem/ruby/3.0.0/bin:$PATH"
fi

mkdir -p "$OUT_DIR"
STAGING_DIR=$(mktemp -d)
trap 'rm -rf "$STAGING_DIR"' EXIT

# Install wheel to staging directory
pip install --target="$STAGING_DIR/usr/lib/python3/dist-packages" "dist/tinyllamax-${VERSION}-py3-none-any.whl"

# Copy console script wrapper
mkdir -p "$STAGING_DIR/usr/bin"
cat > "$STAGING_DIR/usr/bin/tinyllamax" <<'EOF'
#!/usr/bin/env python3
import sys
from tinyllamax.cli import app
if __name__ == '__main__':
    sys.exit(app())
EOF
chmod +x "$STAGING_DIR/usr/bin/tinyllamax"

# Install desktop file
mkdir -p "$STAGING_DIR/usr/share/applications"
cp resources/tinyllamax.desktop "$STAGING_DIR/usr/share/applications/"

# Install icons
for size in 512 256 128 64; do
    mkdir -p "$STAGING_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
    cp "resources/icons/hicolor/${size}x${size}/apps/tinyllamax.png" \
       "$STAGING_DIR/usr/share/icons/hicolor/${size}x${size}/apps/"
done
mkdir -p "$STAGING_DIR/usr/share/icons/hicolor/scalable/apps"
cp resources/icons/tinyllamax.svg "$STAGING_DIR/usr/share/icons/hicolor/scalable/apps/"

# Install man page
mkdir -p "$STAGING_DIR/usr/share/man/man1"
gzip -c man/tinyllamax.1 > "$STAGING_DIR/usr/share/man/man1/tinyllamax.1.gz"

# Build rpm with fpm
fpm -s dir -t rpm \
    -n tinyllamax \
    -v "$VERSION" \
    --description "AI Linux Co-Pilot (propose → simulate → confirm → run)" \
    --url "https://github.com/120git/tinyllama-x" \
    --maintainer "TinyLlama-X <dev@example.com>" \
    --license "MIT" \
    --depends "python3 >= 3.10" \
    --depends "gtk4" \
    --depends "gobject-introspection" \
    --after-install /dev/stdin \
    --chdir "$STAGING_DIR" \
    --package "$OUT_DIR/tinyllamax-${VERSION}-1.noarch.rpm" \
    . <<'POSTINST'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -f /usr/share/icons/hicolor || true
fi
POSTINST

echo "RPM package created: $OUT_DIR/tinyllamax-${VERSION}-1.noarch.rpm"
rpm -qlp "$OUT_DIR/tinyllamax-${VERSION}-1.noarch.rpm" | head -20
