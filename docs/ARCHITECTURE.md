# Architecture

ROBLOX-LX 0.1.0 is a Python CLI built on the standard library. Current priority is the official macOS desktop executable through Darling's Darwin/macOS API translation on Linux, without Android, a guest OS, or a VM.

- `robloxlx.cli`: subcommands, exit codes, local state paths, and fail-closed launch behavior.
- `robloxlx.diagnostics`: read-only Linux host probes plus OpenGL/EGL/Vulkan, audio, input and network tool/library availability.
- `robloxlx.compatibility.darling`: detects installed Darling, maps host paths to `/Volumes/SystemRoot`, builds shell-free argv, supports an existing DPREFIX, captures output to mode-0600 logs, and waits/reaps or terminates the process group.
- `tests/unit`: mocked backend tests and a standalone Mach-O syscall fixture with an integration run that requires installed Darling.

The launcher never changes executable bytes and does not implement Roblox-specific shims, protocol changes, or anti-cheat behavior. Darwin API gaps are recorded as UNKNOWN until directly observed on the installed Darling build or an independent macOS fixture. The Darling process can initialize its default DPREFIX on first use; users can specify an existing prefix to control that state. No credentials or account data are handled.
