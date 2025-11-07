#!/usr/bin/env bash
set -euo pipefail

# TinyLlama-X Ubuntu installer
# Installs CLI, desktop entry, and icon for user (~/.local) or system (/usr/local, /opt)

MODE="user" # default
if [[ ${1:-} == "--system" ]]; then
  MODE="system"
elif [[ ${1:-} == "--user" ]]; then
  MODE="user"
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="tinyllama-x"
ICON_SRC="$REPO_DIR/TinyLlama-x_logo.png"
DESKTOP_SRC="$REPO_DIR/resources/tinyllama-x.desktop"
CLI_SRC="$REPO_DIR/bin/tinyllama-x"

if [[ ! -f "$ICON_SRC" ]]; then
  echo "Error: icon not found at $ICON_SRC" >&2
  exit 1
fi

if [[ $MODE == "system" ]]; then
  APP_DIR="/opt/TinyLlama-X"
  CLI_DEST="/usr/local/bin/$APP_NAME"
  APPS_DIR="/usr/share/applications"
  ICON_DIR="/usr/share/icons/hicolor/512x512/apps"
  SUDO=sudo
else
  APP_DIR="$HOME/.local/share/TinyLlama-X"
  CLI_DEST="$HOME/.local/bin/$APP_NAME"
  APPS_DIR="$HOME/.local/share/applications"
  ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
  SUDO=""
  mkdir -p "$HOME/.local/bin"
fi

# Copy application files
$SUDO mkdir -p "$APP_DIR"
# Copy the entire repo contents except .git
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude ".git" "$REPO_DIR/" "$APP_DIR/"
else
  # Fallback to cp if rsync is not available
  $SUDO rm -rf "$APP_DIR"/* || true
  (cd "$REPO_DIR" && tar cf - --exclude .git .) | (cd "$APP_DIR" && tar xpf -)
fi

# Install CLI
$SUDO install -Dm755 "$CLI_SRC" "$CLI_DEST"

# Install icon (rename to match icon theme name)
$SUDO mkdir -p "$ICON_DIR"
$SUDO install -Dm644 "$ICON_SRC" "$ICON_DIR/$APP_NAME.png"

# Install desktop entry
$SUDO mkdir -p "$APPS_DIR"
# Copy and ensure it references our CLI and icon name
TMP_DESKTOP="/tmp/${APP_NAME}.desktop"
# Hint the runtime app dir to the CLI via environment so it doesn't need to guess
SED_EXEC="Exec=env TINYLLAMA_X_DIR=$APP_DIR $APP_NAME"
sed -e "s#^Exec=.*#$SED_EXEC#g" \
  -e "s#^TryExec=.*#TryExec=$APP_NAME#g" \
  -e "s#^Icon=.*#Icon=$APP_NAME#g" \
  "$DESKTOP_SRC" > "$TMP_DESKTOP"
$SUDO install -Dm644 "$TMP_DESKTOP" "$APPS_DIR/${APP_NAME}.desktop"
rm -f "$TMP_DESKTOP"

# Update icon cache if utility exists (optional)
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  # Rebuild icon cache for hicolor theme if available
  THEME_DIR="${ICON_DIR%/512x512/apps}"
  $SUDO gtk-update-icon-cache -q "$THEME_DIR" || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  $SUDO update-desktop-database "$APPS_DIR" || true
fi

cat <<EOF
Installed TinyLlama-X ($MODE mode):
- App dir:   $APP_DIR
- CLI:       $CLI_DEST
- Desktop:   $APPS_DIR/${APP_NAME}.desktop
- Icon:      $ICON_DIR/$APP_NAME.png

Run from terminal:
  $APP_NAME

Find it in your app menu as: TinyLlama-X
EOF
