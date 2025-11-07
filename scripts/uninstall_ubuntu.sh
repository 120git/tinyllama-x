#!/usr/bin/env bash
set -euo pipefail

# TinyLlama-X Ubuntu uninstaller
MODE="user"
if [[ ${1:-} == "--system" ]]; then
  MODE="system"
fi

APP_NAME="tinyllama-x"
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
fi

$SUDO rm -f "$CLI_DEST" || true
$SUDO rm -f "$APPS_DIR/${APP_NAME}.desktop" || true
$SUDO rm -f "$ICON_DIR/${APP_NAME}.png" || true
$SUDO rm -rf "$APP_DIR" || true

echo "TinyLlama-X uninstalled ($MODE mode)."