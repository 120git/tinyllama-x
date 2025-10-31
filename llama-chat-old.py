#!/usr/bin/env python3
from llama_cpp import Llama

# ✅ Load your TinyLlama model
# Make sure this path matches your downloaded file
MODEL_PATH = "/home/xlost/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

print("🔹 Loading TinyLlama model, please wait...")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=6)

print("\n🤖 TinyLlama Chat is ready! Type 'exit' to quit.\n")

conversation = []

while True:
    user_input = input("🧑 You: ").strip()
    if user_input.lower() in ["exit", "quit", "q"]:
        print("👋 Goodbye!")
        break

    # Keep context for multi-turn conversation
    conversation.append({"role": "user", "content": user_input})

    # Build the dialogue context
    prompt = ""
    for msg in conversation:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"

    # Generate a response
    output = llm(prompt, max_tokens=200, temperature=0.7, top_p=0.95)
    reply = output["choices"][0]["text"].strip()

    # Save the assistant's reply for context
    conversation.append({"role": "assistant", "content": reply})

    print(f"🤖 LLaMA: {reply}\n")
