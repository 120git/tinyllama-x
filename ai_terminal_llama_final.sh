#!/bin/bash
# TinyLlama-X Final Terminal AI Script
# Purpose: Launch your AI terminal assistant with banner and chat
# Author: You
# Usage: ./ai_terminal_llama_final.sh

# ===== CONFIGURATION =====
MODEL_PATH="$HOME/tinyllama-x/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LOG_FILE="$HOME/tinyllama-x/conversation.log"
THREADS=6
CONTEXT=2048

# ===== ASCII BANNER =====
cat << 'EOF'
████████╗██╗     ██╗      ██╗        ███████╗██╗  ██╗
╚══██╔══╝██║     ██║      ██║        ██╔════╝██║ ██╔╝
   ██║   ██║     ██║      ██║        █████╗  █████╔╝ 
   ██║   ██║     ██║      ██║        ██╔══╝  ██╔═██╗ 
   ██║   ███████╗███████╗███████╗   ███████╗██║  ██╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚══════╝╚═╝  ╚═╝
                     TL <- X ->

                  Termininja Engaged
EOF

# ===== CHECK MODEL =====
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found at $MODEL_PATH"
    echo "Please download the TinyLlama model and place it there."
    exit 1
fi

# ===== PYTHON VENV CHECK =====
if [ ! -d "$HOME/ai-env" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$HOME/ai-env"
    source "$HOME/ai-env/bin/activate"
    pip install --upgrade pip
    pip install llama-cpp-python
else
    source "$HOME/ai-env/bin/activate"
fi

# ===== CHAT LOOP =====
python3 << EOF
from llama_cpp import Llama
import readline
import os

MODEL_PATH = os.path.expanduser("$MODEL_PATH")
LOG_FILE = os.path.expanduser("$LOG_FILE")

# Initialize model
print("🔹 Loading TinyLlama model, please wait...")
llm = Llama(model_path=MODEL_PATH, n_ctx=$CONTEXT, n_threads=$THREADS)

# Maintain chat memory to prevent repeats
history = []

print("\n🤖 TinyLlama Chat is ready! Type 'exit' to quit.\n")

while True:
    try:
        user_input = input("🧑 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # Prevent repeating same user query
        if history and user_input == history[-1]['user']:
            print("⚠️ You already asked this. Try a different question.")
            continue

        # Generate response
        response = llm(user_input, max_tokens=256)
        output_text = response['choices'][0]['text'].strip()

        # Prevent exact repeated AI responses
        if history and output_text == history[-1]['ai']:
            output_text += " [↻ repeated content skipped]"

        print(f"🤖 TinyLlama: {output_text}\n")

        # Log conversation
        with open(LOG_FILE, "a") as f:
            f.write(f"You: {user_input}\nAI: {output_text}\n\n")

        # Store history
        history.append({'user': user_input, 'ai': output_text})

        # Keep last 20 entries to save memory
        if len(history) > 20:
            history.pop(0)

    except EOFError:
        print("\n👋 Goodbye!")
        break
    except KeyboardInterrupt:
        print("\n👋 Interrupted, exiting...")
        break
EOF
