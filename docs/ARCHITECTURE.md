# Architecture

ROBLOX-LX 0.1.0 is a small Python CLI built on the standard library.

- `robloxlx.cli`: subcommands, exit codes, local state paths, and fail-closed launch behavior.
- `robloxlx.diagnostics`: bounded, read-only host probes with timeouts.
- `tests/unit`: tests for missing optional probes.

No compatibility runtime is controlled yet. The architecture intentionally does not download, patch, inject into, or launch the Roblox executable. A future backend should wrap Darling as an external dependency and test it with authorized, non-Roblox macOS programs before considering any Roblox pathway.
