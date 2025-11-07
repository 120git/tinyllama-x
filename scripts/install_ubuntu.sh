#!/usr/bin/env bash
set -euo pipefail

# TinyLlama-X Ubuntu/Debian installer

usage() {
  cat <<EOF
Usage: $0 [--system | --user]

Installs TinyLlama-X CLI, desktop entry, and icon.

Options:
  --system   Install for all users (requires sudo)
  --user     Install for current user (default)
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

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

APP_NAME="TinyLlama-X"
CLI_NAME="tinyllama-x"
ICON_NAME="tinyllama-x.png"
ICON_SRC="$REPO_DIR/TinyLlama-x_logo.png"
DESKTOP_TEMPLATE="$REPO_DIR/resources/tinyllama-x.desktop"
CLI_SRC="$REPO_DIR/bin/$CLI_NAME"

if [[ ! -f "$CLI_SRC" ]]; then
  echo "Error: CLI launcher not found at: $CLI_SRC" >&2
  exit 1
fi

if [[ ! -f "$DESKTOP_TEMPLATE" ]]; then
  echo "Error: Desktop file template not found at: $DESKTOP_TEMPLATE" >&2
  exit 1
fi

if [[ ! -f "$ICON_SRC" ]]; then
  echo "Warning: Icon not found at $ICON_SRC. Proceeding without installing icon."
fi

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

echo "Installing TinyLlama-X ($MODE)"
echo "- App dir: $APP_DIR"
echo "- Bin dir: $BIN_DIR"
echo "- Desktop: $APP_SHARE/$CLI_NAME.desktop"
echo "- Icon: $ICON_DIR/$ICON_NAME"

# Create directories
$SUDO mkdir -p "$APP_DIR" "$BIN_DIR" "$APP_SHARE" "$ICON_DIR"

# Copy repo to app dir (rsync preferred)
if command -v rsync >/dev/null 2>&1; then
  $SUDO rsync -a --delete "$REPO_DIR/" "$APP_DIR/"
else
  tmp_tar="$(mktemp)"
  tar -C "$REPO_DIR" -cf "$tmp_tar" .
  $SUDO tar -C "$APP_DIR" -xf "$tmp_tar"
  rm -f "$tmp_tar"
fi

# Ensure main scripts are executable
$SUDO find "$APP_DIR" -maxdepth 2 -type f -name "ai_terminal_*.sh" -exec chmod +x {} + || true

# Install CLI
$SUDO install -m 0755 "$CLI_SRC" "$BIN_DIR/$CLI_NAME"

# Install desktop entry (inject Exec with TINYLLAMA_X_DIR)
DESKTOP_OUT="$(mktemp)"
sed "s#@@EXEC@@#env TINYLLAMA_X_DIR=\"$APP_DIR\" $CLI_NAME#g" "$DESKTOP_TEMPLATE" > "$DESKTOP_OUT"
$SUDO install -m 0644 "$DESKTOP_OUT" "$APP_SHARE/$CLI_NAME.desktop"
rm -f "$DESKTOP_OUT"

# Install icon if present
if [[ -f "$ICON_SRC" ]]; then
  $SUDO install -m 0644 "$ICON_SRC" "$ICON_DIR/$ICON_NAME"
fi

# Update desktop and icon caches when available
if command -v update-desktop-database >/dev/null 2>&1; then
  $SUDO update-desktop-database "$APP_SHARE" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  $SUDO gtk-update-icon-cache -f "${ICON_DIR%/512x512/apps}/.." || true
fi

echo "Installation complete. Try launching from your app grid or run: $CLI_NAME"
