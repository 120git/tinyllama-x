#!/usr/bin/env bash
set -euo pipefail

# TinyLlama-X uninstaller

usage() {
  cat <<EOF
Usage: $0 [--system | --user]

Removes TinyLlama-X CLI, desktop entry, icon, and app directory.

Options:
  --system   Uninstall system-wide (requires sudo)
  --user     Uninstall for current user (default)
EOF
}

MODE="user"
if [[ "${1:-}" == "--system" ]]; then
  MODE="system"
elif [[ "${1:-}" == "--user" || -z "${1:-}" ]]; then
  MODE="user"
elif [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage; exit 0
else
  usage; exit 1
fi

APP_NAME="TinyLlama-X"
CLI_NAME="tinyllama-x"
ICON_NAME="tinyllama-x.png"

if [[ "$MODE" == "system" ]]; then
  APP_DIR="/opt/$APP_NAME"
  BIN_DIR="/usr/local/bin"
  APP_SHARE="/usr/share/applications"
  ICON_DIR="/usr/share/icons/hicolor/512x512/apps"
  SUDO=sudo
else
  APP_DIR="$HOME/.local/share/$APP_NAME"
  BIN_DIR="$HOME/.local/bin"
  APP_SHARE="$HOME/.local/share/applications"
  ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
  SUDO=""
fi

echo "Uninstalling TinyLlama-X ($MODE)"

$SUDO rm -f "$BIN_DIR/$CLI_NAME" || true
$SUDO rm -f "$APP_SHARE/$CLI_NAME.desktop" || true
$SUDO rm -f "$ICON_DIR/$ICON_NAME" || true
$SUDO rm -rf "$APP_DIR" || true

if command -v update-desktop-database >/dev/null 2>&1; then
  $SUDO update-desktop-database "$APP_SHARE" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  $SUDO gtk-update-icon-cache -f "${ICON_DIR%/512x512/apps}/.." || true
fi

echo "Uninstall complete."
