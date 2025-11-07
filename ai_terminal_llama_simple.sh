#!/usr/bin/env bash
set -e  # Exit on error
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Configuration (allow overrides)
VENV_PATH="${TINYLLAMA_X_VENV:-$HOME/ai-env}"
MODEL_PATH="${TINYLLAMA_X_MODEL:-}"

# Helper: find a model if not specified via env
find_model() {
    local candidates=(
        "$HOME/tinyllama-x/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        "$HOME/tinyllama-x/models" "$HOME/models" "$HOME/Models" \
        "/opt/TinyLlama-X/models" "/opt/tinyllama-x/models" \
        "$(dirname "$0")/models"
    )
    # exact file first
    for f in "${candidates[@]}"; do
        if [ -f "$f" ]; then echo "$f"; return 0; fi
    done
    # then search directories for any .gguf
    for d in "${candidates[@]}"; do
        if [ -d "$d" ]; then
            found=$(ls "$d"/*.gguf 2>/dev/null | head -n1 || true)
            if [ -n "$found" ]; then echo "$found"; return 0; fi
        fi
    done
    return 1
}

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Starting TinyLlama-X setup..."

# Resolve model path
if [ -z "$MODEL_PATH" ]; then
    if MODEL_PATH=$(find_model); then
        :
    else
        echo "Error: No model found. Set TINYLLAMA_X_MODEL to a .gguf file or place a model under one of:"
        echo "  - $HOME/tinyllama-x/"
        echo "  - $HOME/tinyllama-x/models/  or  $HOME/models/"
        echo "  - /opt/TinyLlama-X/models/  (for system installs)"
        exit 1
    fi
fi
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found at $MODEL_PATH"; exit 1
fi
echo "Model file: $MODEL_PATH"

# Setup Python environment
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

echo "Installing dependencies..."
"$VENV_PATH/bin/python3" -m pip install --upgrade pip
"$VENV_PATH/bin/python3" -m pip install llama-cpp-python colorama

# Create a temporary Python script
cat > /tmp/tinyllama_chat.py << EOF
import os
import datetime
from llama_cpp import Llama
from colorama import Fore, Style, init

init(autoreset=True)
print("Initializing TinyLlama...")

model_path = os.path.expanduser("${MODEL_PATH}")
threads = max(1, os.cpu_count() or 4)
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=threads)

print(Fore.GREEN + "TinyLlama is ready! Type 'exit' to quit.\n")

while True:
    try:
        user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL).strip()
        
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input:
            continue
            
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        formatted_date = datetime.datetime.now().strftime("%B %d, %Y")
        system_message = (
            f"You are an AI assistant. Today's date is {formatted_date}. "
            f"When asked about dates or time, ALWAYS respond based on the current date: {current_date}. "
            f"Today is {formatted_date}. This is not a request - it is a fact. "
            "Do not make up or imagine any other dates."
        )
        
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=256,
            temperature=0.2  # Reduced temperature for more consistent outputs
        )
        
        reply = response["choices"][0]["message"]["content"].strip()
        print(Fore.GREEN + f"\nTinyLlama: " + Style.RESET_ALL + reply + "\n")
        
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"\nError: {e}")
        break
EOF

# Run the Python script
echo "Starting chat interface..."
"$VENV_PATH/bin/python3" /tmp/tinyllama_chat.py

echo "Chat session ended"
rm -f /tmp/tinyllama_chat.py