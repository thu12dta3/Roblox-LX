# Security

ROBLOX-LX is a local diagnostic prototype. It does not request Roblox credentials, download or launch a client, install packages, modify global settings, patch executables, inject code, disable security controls, or manipulate protocols.

Host probes use fixed argument vectors, bounded timeouts, and no shell. `verify` computes a local SHA-256 hash only; it reports authenticity as unknown unless a trusted publisher signature or digest baseline is independently available. A hash by itself does not prove provenance.

Logs are discovered under `$XDG_STATE_HOME/robloxlx/logs` or `~/.local/state/robloxlx/logs`. Cleanup is restricted to `$XDG_CACHE_HOME/robloxlx/tmp` or `~/.cache/robloxlx/tmp`, and refuses to remove a symlink or non-directory at that path.

Report security issues privately to the repository maintainer rather than posting sensitive details publicly.
