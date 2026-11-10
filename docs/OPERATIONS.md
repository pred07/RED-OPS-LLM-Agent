# Operations Reference

## Working directory

Run commands from the repository root. State, chat history, and result paths are relative to that directory.

## Current terminal commands

The current parser in `reasoning_engine/main.py` defines these commands:

| Command | Behavior |
|---|---|
| `python reasoning_engine/main.py monitor` | Starts the Rich terminal monitor and watches the results directory. |
| `python reasoning_engine/main.py clear` | Clears chat history through the chat manager. It does not guarantee removal of all state or result files. |
| `python pt.py monitor` | Routes to the terminal monitor. |
| `python pt.py clear` | Routes to the terminal `clear` command. |

Although `pt.py` currently lists additional internal command names, the `main.py` argument parser only implements `monitor` and `clear`. Treat the other listed names as unsupported until the CLI implements them.

## API and dashboard

Start the API from the repository root:

```bash
python reasoning_engine/api.py
```

The API binds to `0.0.0.0:8000`. The dashboard source under `reasoning_engine/gui/` calls `http://localhost:8000/api`; start it separately with `npm ci` and `npm run dev` from that directory.

Current API routes include state, history, suggestions, chat, and clear operations. There is no authentication or role-based access control in this prototype. Do not expose it outside a controlled local lab.

## Output collection

The watcher handles `.xml`, `.log`, and `.txt` files created under `reasoning_engine/results/`. XML is sent to the Nmap parser; text and logs are scanned with regular expressions for selected markers. Parsing may miss data or misclassify it. Review output manually before using it to make decisions.

## Cleanup

The terminal `clear` command clears chat history. The API's `/api/clear` handler also attempts to remove target state and results. These are different code paths. Back up anything needed and verify local data deletion before treating either operation as a complete secure wipe.
