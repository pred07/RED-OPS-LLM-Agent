# REDOPS — PTLLM-Setup

REDOPS is an experimental, local-first security-assessment workbench that combines a Python command-line interface, a file-based results monitor, a FastAPI service, a Next.js dashboard, and an Ollama-backed reasoning component.

Use it only in systems and labs for which you have explicit authorization. This repository is a prototype, not a hardened multi-agent platform or a production security product.

## What is implemented

- A `pt` command wrapper that runs operator-supplied commands, streams their output, and writes local logs.
- A Rich terminal monitor for current target state and operator chat.
- A background watcher that reads selected XML and text/log files from the results directory and updates local JSON state.
- A FastAPI API and Next.js interface for viewing state/history and sending chat prompts.
- A reasoning component that currently calls a configured Ollama HTTP endpoint. The checked-in application code does not implement an OpenAI client.

## Current scope and limitations

The present source is a single-machine prototype. It does not contain a distributed agent mesh, a reverse-proxy configuration, authentication, or a production deployment model. The watcher uses format-specific parsing and regular expressions; results require operator validation. The application does not independently verify authorization or target scope.

The API currently enables wildcard CORS and binds to `0.0.0.0:8000`. Do not expose it to an untrusted network. The `pt` wrapper invokes commands through a shell and stores command output locally. Review [Security and data handling](docs/SECURITY_AND_DATA.md) before using it.

## Architecture

```text
Operator
  ├─ `pt` / Rich CLI ──> Python reasoning engine ──> Ollama HTTP endpoint
  │                              ▲
  │                              │ local JSON state and chat history
  └─ Next.js dashboard ──> FastAPI service
                                 ▲
  `pt` output files ──> results watcher / parsers
```

See [Architecture](docs/ARCHITECTURE.md) for component boundaries and [Operations reference](docs/OPERATIONS.md) for the current command surface.

## Quick start

The scripts are written for a Linux or WSL environment. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml rich requests watchdog fastapi uvicorn
```

Create a local `reasoning_engine/config.yaml` using the placeholder example in [Configuration](docs/CONFIGURATION.md). That file is intentionally excluded from Git because local configuration may contain credentials. Install and run the dashboard in a separate terminal:

```bash
cd reasoning_engine/gui
npm ci
npm run dev
```

Run the local API from the repository root in another terminal:

```bash
python reasoning_engine/api.py
```

The dashboard uses `http://localhost:8000/api` by default. Review the API exposure warning above before starting the service. See [Operations reference](docs/OPERATIONS.md) for the terminal monitor and limitations of `pt clear`.

## Project map

- `pt` and `pt.py` — command wrapper and local output logging
- `reasoning_engine/main.py` — Rich terminal interface
- `reasoning_engine/api.py` — FastAPI endpoints
- `reasoning_engine/core/` — state, chat, monitoring, and reasoning components
- `reasoning_engine/modules/parsers/` — supported structured-output parser
- `reasoning_engine/gui/` — Next.js dashboard
- `docs/` — architecture, configuration, operations, and security references

## Data and credentials

Runtime state, chat history, tool output, and the local model configuration are not part of this repository. They may contain sensitive target identifiers, account names, or assessment output. Keep them local, access-controlled, and out of issue reports and commits. Never publish API keys.

## License

No `LICENSE` file is included in this repository snapshot. Reuse terms have not been formally declared.
