# Architecture

## System context

REDOPS runs as a local operator workbench. The current source combines a terminal interface, a command wrapper, filesystem-based result ingestion, an HTTP API, a browser dashboard, JSON persistence, and a local Ollama-compatible model endpoint.

```text
┌──────────────────┐       ┌──────────────────────┐
│ Operator         │──────▶│ `pt` / `pt.py`       │
└──────────────────┘       │ command + output log │
                           └──────────┬───────────┘
                                      │ writes files
                                      ▼
                           ┌──────────────────────┐
                           │ results watcher      │
                           │ XML/text parsers     │
                           └──────────┬───────────┘
                                      │ updates
                                      ▼
                           ┌──────────────────────┐
                           │ JSON state + history │
                           └─────────┬────────────┘
                                     │
               ┌─────────────────────┴──────────────────────┐
               ▼                                            ▼
    ┌────────────────────────┐                 ┌────────────────────┐
    │ Rich terminal monitor  │                 │ FastAPI + Next.js  │
    └────────────┬───────────┘                 └─────────┬──────────┘
                 └──────────────────┬────────────────────┘
                                    ▼
                        ┌──────────────────────┐
                        │ Ollama HTTP endpoint │
                        └──────────────────────┘
```

## Components and responsibilities

| Component | Source | Current responsibility |
|---|---|---|
| Command wrapper | `pt.py` | Launches internal CLI commands or runs an operator-supplied shell command while teeing output to a timestamped log. |
| Terminal interface | `reasoning_engine/main.py` | Displays target state and operator chat; parses `monitor` and `clear` subcommands. |
| Result monitor | `reasoning_engine/core/monitor.py` | Watches the local results directory and dispatches files to parsers. |
| Nmap XML parser | `reasoning_engine/modules/parsers/nmap_xml.py` | Extracts structured host/port/service information from XML files. |
| Text log parser | `reasoning_engine/core/monitor.py` | Uses selected regular expressions for host, port, user, credential, and access markers in text/log output. |
| State and chat stores | `reasoning_engine/core/state_manager.py`, `chat_manager.py` | Read and write local JSON records. |
| HTTP API | `reasoning_engine/api.py` | Exposes state, history, suggestions, chat, and clear endpoints for the UI. |
| Dashboard | `reasoning_engine/gui/` | Next.js interface that calls the API at `http://localhost:8000/api`. |
| Reasoning client | `reasoning_engine/core/hybrid_brain.py` | Sends a prompt to an Ollama-compatible `/api/generate` endpoint. |

## Data flow

1. The operator starts the CLI or API from the repository root.
2. The `pt` wrapper writes captured command output under `reasoning_engine/results/` and records a command entry in `reasoning_engine/data/history.log`.
3. The watcher parses new or modified `.xml`, `.log`, and `.txt` files. Its parsers are heuristic; extracted values are not authoritative findings.
4. The state manager writes local JSON state, while the chat manager writes chat history.
5. The terminal or dashboard displays the current state. Chat requests are sent to the configured Ollama endpoint.

The current Ollama prompt summarizes target IPs and access levels together with the operator query. The code does not implement an OpenAI client, a distributed agent protocol, or a reverse-proxy routing layer. No such components should be claimed in project materials unless they are implemented and reviewed.

## Process and network boundaries

The API is currently started on `0.0.0.0:8000`, enables wildcard CORS, and has no authentication layer in the checked-in code. The UI uses localhost, but that does not restrict the API listener to localhost. Treat it as a trusted-lab-only prototype. See [Security and data handling](SECURITY_AND_DATA.md).
