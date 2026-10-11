# Security

The CLI is a local diagnostic prototype. It never requests Roblox credentials, installs packages, changes global settings, patches an executable, injects code, or disables security controls. `launch --program` starts only an explicit existing local macOS executable through a separately installed Darling process. Diagnostic probes use fixed arguments, bounded timeouts, and no shell; program launch also uses an argv vector and does not interpret a shell command.

`verify` computes SHA-256 only and explicitly reports authenticity as UNKNOWN absent a trusted publisher signature or digest. Do not infer authorization from an unchanged hash.

Logs are listed from `$XDG_STATE_HOME/robloxlx/logs` (or `~/.local/state/robloxlx/logs`); Darling launch logs are mode 0600. Temporary cleanup is constrained to `$XDG_CACHE_HOME/robloxlx/tmp` (or `~/.cache/robloxlx/tmp`). No credentials should be placed in logs or config. Darling can initialize its default prefix on first use; use an existing prefix via `--prefix` when a new default prefix must not be created.
