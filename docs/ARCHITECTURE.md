# Architecture

ROBLOX-LX is a Linux-native diagnostic and compatibility-research CLI. The repository intentionally excludes macOS execution paths and does not claim to provide a working Roblox client.

- `robloxlx.cli`: command parsing, exit codes, file hashing, log discovery, and bounded cleanup.
- `robloxlx.diagnostics`: read-only Linux host probes for OS, kernel, GPU, graphical session, Vulkan, and common audio/input/network tools.
- `robloxlx.graphics.vulkan`: bounded `vkcube` smoke test for hardware Vulkan presentation on Wayland/X11.
- `tests/unit`: deterministic tests for diagnostics and Vulkan process handling.
- `.github/workflows`: unit tests, static security checks, and Python compilation.

Subprocess probes use fixed argument vectors, bounded timeouts, and no shell. Diagnostics do not install packages, change global settings, download a client, or request credentials. A successful host Vulkan test is not evidence that Roblox itself is compatible.
