#!/usr/bin/env python3
import os
from llama_cpp import Llama

MODEL_PATH = os.path.expanduser('~/tinyllama-x/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf')
HISTORY_LOG = os.path.expanduser('~/tinyllama-x/conversation.log')

# Initialize model
print("🔹 Loading TinyLlama model, please wait...")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=6)
print("🤖 TinyLlama Chat is ready! Type 'exit' to quit.\n")

previous_responses = set()

while True:
    try:
        user_input = input("🧑 You: ").strip()
    except EOFError:
        print("\n👋 Goodbye!")
        break

    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # Generate response
    response = llm(user_input, max_tokens=150)
    text = response.get('text', '').strip()

    # Avoid repeated answers
    if text in previous_responses:
        print("🤖 TinyLlama: (duplicate response suppressed)\n")
        continue
    previous_responses.add(text)

    # Print and log response
    print(f"🤖 TinyLlama: {text}\n")
    with open(HISTORY_LOG, "a") as f:
        f.write(f"User: {user_input}\nAssistant: {text}\n\n")
