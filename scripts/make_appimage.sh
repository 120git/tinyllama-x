#!/usr/bin/env bash
set -euo pipefail

# Build AppImage using appimage-builder

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

# Check for appimage-builder
if ! command -v appimage-builder &> /dev/null; then
    echo "appimage-builder not found. Installing..."
    pip install --user appimage-builder
    export PATH="$HOME/.local/bin:$PATH"
fi

mkdir -p "$OUT_DIR"

# Create AppDir structure
APPDIR="$PROJECT_ROOT/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/512x512/apps"

# Install Python and dependencies
mkdir -p "$APPDIR/usr/lib/python3/dist-packages"
pip install --target="$APPDIR/usr/lib/python3/dist-packages" "dist/tinyllamax-${VERSION}-py3-none-any.whl"

# Create AppRun launcher
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$APPDIR/usr/lib/python3/dist-packages:$PYTHONPATH"
export PATH="$APPDIR/usr/bin:$PATH"
exec python3 -m tinyllamax.cli "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Copy desktop file
cp resources/tinyllamax.desktop "$APPDIR/tinyllamax.desktop"
cp resources/tinyllamax.desktop "$APPDIR/usr/share/applications/"

# Copy icon
cp resources/icons/hicolor/512x512/apps/tinyllamax.png "$APPDIR/tinyllamax.png"
cp resources/icons/hicolor/512x512/apps/tinyllamax.png "$APPDIR/usr/share/icons/hicolor/512x512/apps/"

# Create appimage-builder recipe
cat > "$PROJECT_ROOT/AppImageBuilder.yml" <<EOF
version: 1
script:
  - echo "AppImage build script"

AppDir:
  path: ./AppDir
  app_info:
    id: com.github.120git.tinyllamax
    name: TinyLlama-X
    icon: tinyllamax
    version: ${VERSION}
    exec: usr/bin/python3
    exec_args: "-m tinyllamax.cli \\\$@"

  apt:
    arch: amd64
    sources:
      - sourceline: 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse'
    include:
      - python3
      - python3-gi
      - gir1.2-gtk-4.0
    exclude:
      - adwaita-icon-theme
      - humanity-icon-theme

  files:
    exclude:
      - usr/share/man
      - usr/share/doc/*/README.*
      - usr/share/doc/*/changelog.*
      - usr/share/doc/*/NEWS.*
      - usr/share/doc/*/TODO.*

  runtime:
    env:
      PYTHONHOME: '\${APPDIR}/usr'
      PYTHONPATH: '\${APPDIR}/usr/lib/python3/dist-packages'

AppImage:
  arch: x86_64
  update-information: guess
EOF

# Build AppImage
appimage-builder --recipe "$PROJECT_ROOT/AppImageBuilder.yml" --skip-test

# Move to out directory
if [ -f "TinyLlamaX-${VERSION}-x86_64.AppImage" ]; then
    mv "TinyLlamaX-${VERSION}-x86_64.AppImage" "$OUT_DIR/"
elif [ -f "TinyLlama_X-${VERSION}-x86_64.AppImage" ]; then
    mv "TinyLlama_X-${VERSION}-x86_64.AppImage" "$OUT_DIR/TinyLlamaX-${VERSION}-x86_64.AppImage"
else
    # Find any .AppImage file created
    find . -maxdepth 1 -name "*.AppImage" -exec mv {} "$OUT_DIR/TinyLlamaX-${VERSION}-x86_64.AppImage" \;
fi

# Cleanup
rm -rf "$APPDIR" "$PROJECT_ROOT/AppImageBuilder.yml"

echo "AppImage created: $OUT_DIR/TinyLlamaX-${VERSION}-x86_64.AppImage"
ls -lh "$OUT_DIR/"*.AppImage || true
