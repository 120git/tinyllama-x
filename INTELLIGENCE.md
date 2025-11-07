# TinyLlama-X Intelligence Features

## 🧠 What's New: Smart Assistant Mode

TinyLlama-X now includes an intelligent assistant layer with:

### Intent Detection
Automatically understands what you want to do:
- **Package Management**: "install git", "remove firefox", "update my system"
- **Command Help**: "what does rsync do?", "explain chmod"
- **System Info**: "what distro am I using?"
- **General Chat**: Ask any Linux question

### Distro-Aware Adapters
Automatically detects your Linux distribution and uses the right package manager:
- Ubuntu/Debian → apt
- Fedora/RHEL → dnf
- Arch/Manjaro → pacman
- openSUSE → zypper
- And more...

### Safe Execution Pipeline
Every system operation follows: **Propose → Confirm → Simulate → Run**

- **Risk Assessment**: Color-coded LOW/MEDIUM/HIGH risk levels
- **Dry-Run Support**: See what will happen before executing
- **Undo Hints**: Suggestions for reversing changes
- **Confirmation Gates**: No destructive ops without explicit approval

### RAG-Lite Command Help
Get instant examples and safety warnings:
- Fetches tldr pages (cached locally)
- Falls back to man page summaries
- Built-in safety warnings for dangerous commands (rm, dd, chmod, etc.)

### Operation History
All actions logged to SQLite (~/.cache/tinyllama-x/history.db):
- Track last 20+ operations
- Find similar failures for troubleshooting
- Success rate statistics by intent type

---

## 🚀 Usage

### Run Smart Assistant
```bash
./ai_terminal_llama_smart.sh
```

### Example Interactions

**Package Installation:**
```
You: install htop
[Intent: package_install, confidence: 95%]
📍 Detected: Ubuntu 22.04 (apt)

EXECUTION PLAN
═══════════════════════════════════════════════
Description: Install 'htop' using apt
Command:     sudo apt install htop
Risk Level:  MEDIUM
Undo Hint:   Undo: sudo apt remove <package>
═══════════════════════════════════════════════

Proceed with this operation? [y/N]:
```

**Command Explanation:**
```
You: what does rsync do?
[Intent: command_explain, confidence: 90%]

━━━ RSYNC ━━━

A fast, versatile file copying tool for local and remote destinations.

Examples:

1. Transfer file from local to remote host
  rsync path/to/local_file remote_host:path/to/remote_directory

2. Sync local directory to remote (delete removed files)
  rsync -avz --delete path/to/local_directory remote_host:path/to/remote_directory

3. Transfer with progress and bandwidth limit
  rsync -avz --progress --bwlimit=1000 path/to/local_file remote_host:path/to/remote_directory

Source: tldr
```

**System Update:**
```
You: update my system
[Intent: system_update, confidence: 95%]

EXECUTION PLAN
═══════════════════════════════════════════════
Description: Update Ubuntu 22.04 system packages
Command:     sudo apt update && sudo apt upgrade
Risk Level:  MEDIUM
⚠️  Requires root privileges
═══════════════════════════════════════════════

Proceed with this operation? [y/N]:
```

---

## 🔧 Environment Variables

- `TINYLLAMA_X_MODEL` - Path to your GGUF model
- `TINYLLAMA_X_VENV` - Python virtualenv path (default: ~/ai-env)
- `TINYLLAMA_X_THREADS` - CPU threads for inference (default: auto-detect)

---

## 📦 Architecture

```
tinyllama-x/
├── lib/
│   ├── intent.py         # Intent classification with regex + keywords
│   ├── distro.py         # /etc/os-release parsing (FreeDesktop spec)
│   ├── pm_adapter.py     # Package manager adapters with dry-run
│   ├── rag.py            # tldr + man page integration
│   ├── executor.py       # Safe execution with risk assessment
│   └── history.py        # SQLite operation logging
├── tinyllama_x_smart.py  # Enhanced chat loop
└── ai_terminal_llama_smart.sh  # Launcher script
```

---

## 🛡️ Safety Features

### Risk Levels
- **LOW** (green): Read-only operations, auto-confirmable
- **MEDIUM** (yellow): Reversible changes, requires 'y'
- **HIGH** (red): Destructive ops, requires typing 'yes'

### Dangerous Commands
Built-in warnings for:
- `rm -rf` - Recursive deletion
- `dd` - Disk operations
- `mkfs` - Filesystem formatting
- `chmod 777` - Permission issues
- `systemctl stop` - Service disruption
- And more...

### Confirmation Flow
1. Show command preview
2. Display risk level + undo hint
3. Run dry-run simulation (if supported)
4. Ask for explicit confirmation
5. Execute and log result

---

## 🧪 Testing

Test distro detection:
```bash
python3 -c "from lib.distro import detect_distro; print(detect_distro())"
```

Test intent classification:
```bash
python3 -c "from lib.intent import classify_intent; print(classify_intent('install git'))"
```

Test command help:
```bash
python3 -c "from lib.rag import explain_command; help=explain_command('rsync'); print(help.description if help else 'Not found')"
```

---

## 📝 Notes

- All operations logged to `~/.cache/tinyllama-x/history.db`
- tldr pages cached in `~/.cache/tinyllama-x/tldr/`
- Conversation log: `~/tinyllama-x/conversation.log`
- Safe to test: dry-run mode available for apt, dnf, zypper

---

## 🔮 Future Enhancements

- [ ] Multi-step workflows (chain operations)
- [ ] Rollback capability with automatic snapshots
- [ ] LLM-powered intent classification for edge cases
- [ ] Plugin system for custom intents
- [ ] Web UI with execution history visualization
- [ ] Integration with systemd service management
- [ ] File operation templates (backup, sync patterns)

---

## 📜 License

MIT License - Same as TinyLlama-X core
