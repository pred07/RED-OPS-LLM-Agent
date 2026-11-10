# Configuration Reference

## Local model endpoint

`reasoning_engine/main.py` loads `reasoning_engine/config.yaml` relative to the repository root. If the file is missing or invalid, it uses a built-in Ollama URL and model fallback. `reasoning_engine/api.py` currently constructs the reasoning client with a localhost Ollama URL.

Create the ignored local file with a minimal configuration:

```yaml
ollama:
  url: "http://127.0.0.1:11434"
  model: "llama3"
```

The model must already be available to the Ollama service. Host addressing differs between native Linux, WSL, and containers; use the address reachable from the process running REDOPS.

## Credentials

Do not add secrets to Git, documentation, screenshots, or issue reports. The local `config.yaml` is ignored. The current application source reads only the `ollama` settings from this file; an OpenAI configuration block in an older local config is not evidence of an implemented OpenAI client.

## Python dependencies

The current source imports `PyYAML`, `rich`, `requests`, `watchdog`, `fastapi`, and `uvicorn`. Install them into an isolated Python virtual environment. There is not currently a pinned Python requirements file in the repository snapshot.

## Dashboard dependencies

The Next.js dashboard manifest and lockfile are under `reasoning_engine/gui/`. Use `npm ci` there for a lockfile-based install. The UI API base is currently hardcoded to `http://localhost:8000/api` in `src/app/page.tsx`.

## Local data paths

The application creates these paths relative to the working directory:

- `reasoning_engine/data/state.json` — parsed target state;
- `reasoning_engine/data/chat_history.json` — chat messages;
- `reasoning_engine/data/history.log` — command history from the wrapper;
- `reasoning_engine/results/` — captured tool output.

These paths are ignored by Git. Keep the process working directory at the repository root so the relative paths resolve as expected.
