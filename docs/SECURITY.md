# Security

The CLI is a local diagnostic prototype. It never requests Roblox credentials, installs packages, changes global settings, starts the Roblox client, or disables security controls. Diagnostic subprocess calls use argument arrays, bounded timeouts, and no shell.

`verify` computes SHA-256 only and explicitly reports authenticity as UNKNOWN absent a trusted publisher signature or digest. Do not infer authorization from an unchanged hash.

Logs are listed from `$XDG_STATE_HOME/robloxlx/logs` (or `~/.local/state/robloxlx/logs`). Temporary cleanup is constrained to `$XDG_CACHE_HOME/robloxlx/tmp` (or `~/.cache/robloxlx/tmp`). No credentials should be placed in logs or config.
