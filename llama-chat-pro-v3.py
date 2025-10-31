#!/usr/bin/env python3
import os
import glob
import time
from llama_cpp import Llama

# ------------------------
# Suppress llama_cpp verbose logs
# ------------------------
os.environ["LLAMA_CPP_VERBOSE"] = "0"

# ------------------------
# Auto-detect GGUF model
# ------------------------
MODEL_DIR = os.path.expanduser("~/models")
model_files = glob.glob(os.path.join(MODEL_DIR, "*.gguf"))
if not model_files:
    print("\033[91m❌ No GGUF models found in ~/models. Please add a model and try again.\033[0m")
    exit(1)

MODEL_PATH = model_files[-1]  # Use the last (newest) file
print(f"\033[94m🔹 Loading model: {MODEL_PATH}\033[0m")

# ------------------------
# Initialize model
# ------------------------
llm = Llama(model_path=MODEL_PATH, n_ctx=1024, n_threads=6)
print("\033[92m✅ Model loaded successfully!\033[0m")
print("\033[96m💬 TinyLlama Chat is ready! Type 'exit' to quit or '/reset' to clear conversation.\033[0m\n")

# ------------------------
# Conversation log file
# ------------------------
log_file = os.path.expanduser("~/ai-terminal/conversation.log")
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

# ------------------------
# System instruction
# ------------------------
SYSTEM_MSG = {
    "role": "system",
    "content": (
        "You are a helpful AI assistant. "
        "Do not assume the user wants to create accounts or follow platform-specific instructions "
        "unless explicitly asked. Focus on general, helpful responses."
    )
}

conversation = [SYSTEM_MSG.copy()]

# ------------------------
# Typing animation helper
# ------------------------
def type_print(text, delay=0.02):
    for c in text:
        print(c, end="", flush=True)
        time.sleep(delay)
    print()

# ------------------------
# Main conversation loop
# ------------------------
while True:
    user_input = input("\033[93m🧑 You:\033[0m ").strip()

    # Exit command
    if user_input.lower() in ["exit", "quit", "q"]:
        print("\033[95m👋 Goodbye!\033[0m")
        break

    # Reset conversation
    if user_input.lower() == "/reset":
        conversation = [SYSTEM_MSG.copy()]
        print("\033[95m🔄 Conversation context has been reset!\033[0m\n")
        continue

    conversation.append({"role": "user", "content": user_input})
    with open(log_file, "a") as f:
        f.write(f"User: {user_input}\n")

    # Build dialogue context
    prompt = ""
    for msg in conversation:
        role = "User" if msg["role"] == "user" else "Assistant" if msg["role"] == "assistant" else "System"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"

    # Generate response
    output = llm(prompt, max_tokens=200, temperature=0.7, top_p=0.95)
    reply = output["choices"][0]["text"].strip()

    conversation.append({"role": "assistant", "content": reply})
    with open(log_file, "a") as f:
        f.write(f"TinyLlama: {reply}\n")

    # Print with typing effect
    print("\033[92m🤖 TinyLlama:\033[0m ", end="")
    type_print(reply)
