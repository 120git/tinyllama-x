# ![Lucky Llama-x Logo](assets/TinyLlama-x_logo.png)
# 🐱‍💻 TinyLlama-X

**TinyLlama-X** is an all-in-one terminal AI companion for Linux, designed to assist users from **Linux newcomers to advanced users**. It leverages TinyLlama models to provide interactive AI functionality directly in your terminal, without the need for web browsers or cloud services.

---

## 🚀 Features

- **Text Generation** – Ask questions or generate text using TinyLlama models.  
- **Interactive Terminal AI** – Engage in a chat-like interface directly in your Linux terminal.  
- **Lightweight and Local** – Runs fully locally, using minimal resources.  
- **Flexible Scripts** – Multiple entry scripts for auto-start, advanced usage, and testing.  
- **Model Management** – Easily switch between TinyLlama models.  
- **ASCII Logo & Branding** – Fun terminal banner when starting the app.

---

## 🛠 Installation

1. Clone the repository:

```bash
git clone https://github.com/120git/tinyllama-x.git
cd tinyllama-x

2. Create a Python virtual environment:

python3 -m venv ai-env
source ai-env/bin/activate


3. Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt


4. Download or place your TinyLlama model in the models/ folder:

models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

💻 Usage

Start the TinyLlama-X terminal app:

./ai_terminal_llama.sh

r for auto-start with your preferred model:

./ai_terminal_llama_auto.sh


Exit anytime by typing:

exit


📂 File Structure

tinyllama-x/
├─ ai_terminal.sh                  # Main AI terminal script
├─ ai_terminal_llama.sh            # Llama chat script
├─ ai_terminal_llama_auto.sh       # Auto-start Llama script
├─ run-llama.py                    # TinyLlama launcher
├─ run-tinyllama.py                # TinyLlama launcher
├─ models/                         # Folder for Llama models
│  └─ tinyllama-1.1b-chat.v1.Q4_K_M.gguf
├─ output/                         # Generated outputs/logs
├─ README.md                        # This file
└─ LICENSE                         # MIT License


⚡ Recommended Workflow

1. Activate the environment:

source ai-env/bin/activate

2. Launch your preferred script:

./ai_terminal_llama.sh


3. Chat, explore AI capabilities, or test text generation.

📝 Notes

Keep large model files out of Git repository; include them in .gitignore.

Ensure pip and Python are updated for best performance.

Terminal is optimized for Linux but should work on macOS with minor adjustments.

📜 License

This project is licensed under the MIT License. See LICENSE
 for details.

👾 ASCII Logo

  TL  <-X->

Termininja Engaged


