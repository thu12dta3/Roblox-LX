# Development

Requires Python 3.10 or newer. Install locally with `python -m pip install -e .`. Run `python -m unittest discover -s tests/unit` and `robloxlx doctor`.

Diagnostics are read-only and subprocess probes have a short timeout. Do not add downloads, privileged commands, client modifications, secret capture, anti-cheat evasion, or protocol manipulation. Keep tests independent of Roblox credentials and production game servers.

Use Conventional Commit subjects (`feat:`, `fix:`, `docs:`, `test:`, `build:`, `chore:`). Development branch: `codex/bootstrap-roblox-lx`.
