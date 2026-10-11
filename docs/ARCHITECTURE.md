# Architecture

ROBLOX-LX 0.1.0 is a small Python CLI built on the standard library. The agreed runtime direction is the official Windows desktop client with Windows API translation through Wine; no Windows/macOS guest OS or VM is used.

- `robloxlx.cli`: subcommands, exit codes, local state paths, and fail-closed launch behavior.
- `robloxlx.diagnostics`: bounded, read-only Linux host, graphics, and Wine availability probes with timeouts.
- `robloxlx.compatibility.wine`: discovers user-installed Wine and builds an argv vector for an existing local Windows program; it does not execute it or handle Roblox launch.
- `tests/unit`: tests for missing optional probes.

No Roblox runtime is controlled. Wine is an external API-translation runtime, not a Windows guest OS. Future integration must keep the Roblox executable unchanged and invoke user-installed Wine as a separate process. No credentials or account data are handled. Hyperion's documented Wine incompatibility blocks real Roblox launch; only benign independent Windows programs may be used for early runtime tests. Darling, macOS clients, mobile clients, and VMs are excluded.
