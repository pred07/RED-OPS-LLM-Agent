# Security and Data Handling

## Authorization boundary

Use REDOPS only for assets and labs explicitly authorized for assessment. The application does not verify ownership, scope, or permission. The operator is responsible for target allowlists, engagement rules, and stop conditions.

## Local records

The wrapper stores command output in timestamped files under `reasoning_engine/results/` and appends command text, exit status, log filename, and duration to `reasoning_engine/data/history.log`. The monitor extracts selected host, port, user, credential, and access markers into local state and chat history. These files can therefore contain sensitive network and account information.

Protect the workspace with appropriate file permissions. Review and sanitize logs, screenshots, and state before sharing. The repository ignores runtime JSON/log files and local configuration so they are not added accidentally.

## Command execution

`pt.py` accepts operator-provided arguments, joins them into a string, and invokes `subprocess.Popen(..., shell=True)`. This executes through the host shell and is not safe for untrusted arguments or remote multi-user access. Do not pass untrusted data to the wrapper and do not run it as a privileged service.

## API exposure

The API currently:

- listens on `0.0.0.0:8000`;
- allows all CORS origins;
- has no authentication or authorization middleware in the checked-in source;
- exposes state/history and a clear route.

The dashboard's use of `localhost` does not limit the server listener. Keep this service in an isolated, trusted lab and use host firewall controls. Do not publish it to the internet or claim it is protected by a reverse proxy; no reverse-proxy configuration is included.

## Model and data transfer

The current reasoning implementation posts prompts to the configured Ollama-compatible HTTP endpoint. Run Ollama locally or on a trusted host and confirm its network boundary. The checked-in source does not include an OpenAI client. Do not put provider keys in tracked files; keep local configuration ignored.

## Retention and deletion

No retention schedule is implemented. Operators must set an engagement-specific retention period, securely remove expired outputs and local state, and account for backups. The clear commands have different scopes; see [Operations reference](OPERATIONS.md).

## Not a security guarantee

This project is experimental. Its parsers use heuristics, its state is file-based, and its HTTP API and command wrapper are not hardened for production. It does not replace human review, approved tooling, or organizational security controls.
