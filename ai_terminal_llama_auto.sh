#!/usr/bin/env bash
# ===============================================================
# 🧠 TinyLlama-X Interactive AI Terminal
# Author: 120git
# Version: v4.2.0
# Description: Interactive AI chat assistant for Linux terminal.
# ===============================================================

# === CONFIGURATION ===
MODEL_PATH="$HOME/tinyllama-x/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LOG_FILE="$HOME/tinyllama-x/conversation.log"
THREADS=6
CONTEXT=2048
VENV_PATH="$HOME/ai-env"

# === ASCII TITLE ===
clear
cat << "EOF"
████████╗██╗     ██╗      ██╗        ███████╗██╗  ██╗
╚══██╔══╝██║     ██║      ██║        ██╔════╝██║ ██╔╝
   ██║   ██║     ██║      ██║        █████╗  █████╔╝ 
   ██║   ██║     ██║      ██║        ██╔══╝  ██╔═██╗ 
   ██║   ███████╗███████╗███████╗   ███████╗██║  ██╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚══════╝╚═╝  ╚═╝
                     TL <- X ->

                  Termininja Engaged
===============================================================
EOF

# === VALIDATION ===
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found at: $MODEL_PATH"
    echo "Please ensure TinyLlama GGUF model is downloaded correctly."
    read -rp "Press Enter to exit..."
    exit 1
fi

# === SETUP PYTHON ENVIRONMENT ===
if [ ! -d "$VENV_PATH" ]; then
    echo "⚙️  Creating Python environment..."
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

pip install --quiet --upgrade pip
pip install --quiet llama-cpp-python colorama

# === LOG ROTATION (KEEP LAST 7 SESSIONS) ===
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d-%H%M%S)"
    ls -t "$HOME"/tinyllama-x/conversation.log.* 2>/dev/null | tail -n +8 | xargs -r rm --
fi

# === RUN PYTHON CHAT INTERFACE ===
python3 << 'EOF'
import os, datetime, sys
from colorama import Fore, Style, init
from llama_cpp import Llama

init(autoreset=True)

MODEL_PATH = os.path.expanduser("~/tinyllama-x/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
LOG_FILE = os.path.expanduser("~/tinyllama-x/conversation.log")

print(Fore.YELLOW + "\n🔹 Loading TinyLlama model, please wait...\n")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=6)

print(Fore.GREEN + "\n🤖 TinyLlama Chat is ready! Type 'exit' to quit.\n")

# Log session start
with open(LOG_FILE, "a") as f:
    f.write(f"\n=== New Session: {datetime.datetime.now()} ===\n")

# Chat loop
while True:
    try:
        sys.stdout.write(Fore.CYAN + "🧑 You: " + Style.RESET_ALL)
        sys.stdout.flush()

        user_input = sys.stdin.readline().strip()
        if not user_input:
            print(Fore.RED + "(No input detected — type something or 'exit')")
            continue
        if user_input.lower() in ["exit", "quit"]:
            print(Fore.MAGENTA + "👋 Goodbye, ninja.")
            break

        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": user_input}],
            max_tokens=256,
            temperature=0.7
        )
        reply = response["choices"][0]["message"]["content"].strip()
        print(Fore.GREEN + f"\n🤖 TinyLlama: " + Style.RESET_ALL + reply + "\n")

        with open(LOG_FILE, "a") as f:
            f.write(f"You: {user_input}\nTinyLlama: {reply}\n")

    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Interrupted by user.")
        break
    except EOFError:
        print(Fore.RED + "\n⚠️ EOF detected (no TTY input). Keeping window open.")
        input("Press Enter to close... ")
        break
EOF

# Keep terminal open if launched from GUI
read -rp "Press Enter to close TinyLlama-X..."
