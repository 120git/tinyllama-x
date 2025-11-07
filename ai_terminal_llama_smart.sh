#!/usr/bin/env bash
set -euo pipefail

# TinyLlama-X Smart Assistant Launcher
# Integrates intent detection, distro adapters, and safe execution

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
MODEL_PATH="${TINYLLAMA_X_MODEL:-$HOME/tinyllama-x/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf}"
VENV_PATH="${TINYLLAMA_X_VENV:-$HOME/ai-env}"

# ASCII Banner
clear
cat << 'EOF'
████████╗██╗███╗   ██╗██╗   ██╗██╗     ██╗      █████╗ ███╗   ███╗ █████╗       ██╗  ██╗
╚══██╔══╝██║████╗  ██║╚██╗ ██╔╝██║     ██║     ██╔══██╗████╗ ████║██╔══██╗      ╚██╗██╔╝
   ██║   ██║██╔██╗ ██║ ╚████╔╝ ██║     ██║     ███████║██╔████╔██║███████║█████╗ ╚███╔╝ 
   ██║   ██║██║╚██╗██║  ╚██╔╝  ██║     ██║     ██╔══██║██║╚██╔╝██║██╔══██║╚════╝ ██╔██╗ 
   ██║   ██║██║ ╚████║   ██║   ███████╗███████╗██║  ██║██║ ╚═╝ ██║██║  ██║      ██╔╝ ██╗
   ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝      ╚═╝  ╚═╝
                                                                                          
                    🧠 Intelligent Linux Terminal Assistant
              Intent Detection • Distro Adapters • Safe Execution • RAG-lite
===============================================================================
EOF

# Validation
echo "Checking model: $MODEL_PATH"
if [[ ! -f "$MODEL_PATH" ]]; then
    echo "❌ Model not found at: $MODEL_PATH"
    echo "   Set TINYLLAMA_X_MODEL to your GGUF model path."
    read -rp "Press Enter to exit..."
    exit 1
fi
echo "✅ Model found"

# Setup Python environment
echo "Setting up environment: $VENV_PATH"
if [[ ! -d "$VENV_PATH" ]]; then
    echo "⚙️  Creating virtual environment..."
    python3 -m venv "$VENV_PATH" || { echo "Failed to create venv"; exit 1; }
fi

echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate" || { echo "Failed to activate venv"; exit 1; }

echo "Installing/updating dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet llama-cpp-python colorama numpy
echo "✅ Environment ready"

# Run smart assistant
export TINYLLAMA_X_MODEL="$MODEL_PATH"
export TINYLLAMA_X_THREADS="${TINYLLAMA_X_THREADS:-$(nproc 2>/dev/null || echo 4)}"

python3 "$SCRIPT_DIR/tinyllama_x_smart.py" "$@"

# Keep terminal open if launched from GUI
read -rp "Press Enter to close..."
