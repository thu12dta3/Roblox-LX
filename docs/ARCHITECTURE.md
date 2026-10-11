# Architecture

ROBLOX-LX 0.1.0 is a small Python CLI built on the standard library. The product requirement is a native Linux Roblox client with no VM, emulator, or OS API translation layer.

- `robloxlx.cli`: subcommands, exit codes, local state paths, and fail-closed launch behavior.
- `robloxlx.diagnostics`: bounded, read-only Linux host and graphics probes with timeouts.
- `tests/unit`: tests for missing optional probes.

No Roblox runtime is controlled. The architecture intentionally does not download, patch, inject into, or launch the Roblox executable, and does not use Wine, Darling, a VM, or an emulator. A native launcher can only be implemented when Roblox provides a Linux client or an official supported interface for one. Until then, development is limited to independent host diagnostics and documentation; the product goal is blocked externally.
