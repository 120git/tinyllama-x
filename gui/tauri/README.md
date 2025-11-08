# TinyLlama-X Tauri Desktop App (Scaffold)

This directory contains a minimal Tauri application scaffold for TinyLlama-X.
The Tauri app provides an alternative desktop interface using Rust + JavaScript/TypeScript.

## Status

🚧 **Scaffold Only** - This is a basic structure template. Full implementation pending.

## Architecture

```
gui/tauri/
├── src/              # Frontend (HTML/CSS/JS or framework of choice)
├── src-tauri/        # Rust backend
│   ├── src/
│   │   └── main.rs   # Tauri main entry point
│   ├── Cargo.toml    # Rust dependencies
│   └── tauri.conf.json  # Tauri configuration
└── README.md
```

## Planned Integration

The Tauri app will integrate with TinyLlama-X via one of these approaches:

### Option 1: IPC Bridge (Recommended)
- Python HTTP bridge using FastAPI
- Tauri frontend calls REST endpoints
- Endpoints map to presenter functions (classify, plan, simulate, execute, etc.)

```
Tauri UI → HTTP → FastAPI Bridge → TinyLlamaPresenter → Core
```

### Option 2: Shell Commands
- Use `tauri-plugin-shell` with strict allowlist
- Call Python CLI entrypoints directly
- Parse stdout/stderr for results

```
Tauri UI → Shell Plugin → `tinyllamax plan --install htop` → Parse Output
```

## Prerequisites

- [Rust](https://www.rust-lang.org/tools/install) (cargo)
- [Node.js](https://nodejs.org/) (npm/yarn) - if using a JS framework
- [Tauri CLI](https://tauri.app/v1/guides/getting-started/prerequisites)

```bash
# Install Tauri CLI
cargo install tauri-cli

# Or via npm
npm install -g @tauri-apps/cli
```

## Development

### Initial Setup (To Be Implemented)

```bash
cd gui/tauri

# Initialize Tauri project
npm create tauri-app
# Or
cargo tauri init

# Install dependencies
npm install
# Or add Rust dependencies in Cargo.toml

# Start development server
cargo tauri dev
# Or
npm run tauri dev
```

### Build Production

```bash
cargo tauri build
# Or
npm run tauri build
```

## UI Layout (Planned)

The Tauri UI will replicate the GTK interface:

- **Input Section**: Command text box
- **Options**: Backend selector, model input, simulate-only checkbox
- **Buttons**: Propose/Simulate, Run, Cancel, Explain, History
- **Display**: Planned command panel, output console
- **Status Bar**: System info (distro, package manager)

## Integration Example

### FastAPI Bridge (Python)

```python
# bridge.py
from fastapi import FastAPI
from tinyllamax.gui.presenter import TinyLlamaPresenter
from tinyllamax.model_backends.ollama import OllamaBackend

app = FastAPI()
presenter = TinyLlamaPresenter(OllamaBackend())

@app.post("/classify")
async def classify(text: str):
    intent = presenter.classify_intent(text)
    return {"intent": intent.model_dump()}

@app.post("/simulate")
async def simulate():
    result = presenter.simulate_plan(presenter.current_plan)
    return {"output": result.summary}
```

### Tauri Frontend (JavaScript)

```javascript
// src/main.js
import { invoke } from '@tauri-apps/api/tauri';

async function propose(userText) {
    const response = await fetch('http://localhost:8000/classify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: userText})
    });
    const data = await response.json();
    console.log('Intent:', data.intent);
}
```

## Security Considerations

- Validate all inputs from frontend
- Use CORS restrictions for HTTP bridge
- Implement authentication if exposed beyond localhost
- Audit shell command allowlist (if using shell approach)
- Never use `shell=True` or execute arbitrary commands

## References

- [Tauri Documentation](https://tauri.app/v1/guides/)
- [Tauri IPC](https://tauri.app/v1/guides/features/command)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tauri + Python](https://tauri.app/v1/guides/building/sidecar)

## Contributing

To implement the full Tauri app:

1. Initialize a Tauri project in this directory
2. Implement the FastAPI bridge or shell command integration
3. Create the frontend UI matching the GTK layout
4. Add proper error handling and state management
5. Update this README with actual usage instructions
