# Feasibility and scope — 2026-10-11

The current engineering target is the original Roblox macOS desktop executable through Darling's macOS/Darwin API translation on Linux. Android/tablet clients and full OS virtual machines are excluded. ROBLOX-LX does not patch the client, inject shims, alter anti-cheat or spoof network protocols.

## Findings

- Darling is an external macOS compatibility runtime for Linux. Its README describes a Mach-O loader, `darlingserver` for Mach IPC/POSIX/Darwin calls, and reimplementations of Foundation, AppKit, CoreAudio and CoreFoundation. GUI support remains in development; its initial Metal path translates through Vulkan. These upstream statements describe the project, not compatibility with Roblox.
- Darling was not found on this development host. It was not installed because package/system changes are outside the authorized diagnostic scope.
- The host has Clang 23.1.1 and LLD's `ld64.lld` 23.1.1. A self-authored x86_64 Mach-O syscall fixture compiled and linked successfully, and its Mach-O 64-bit magic was verified. It was not executable-tested because Darling is absent.
- MacOBlox is an independent Darling launcher. Its repository identifies MIT licensing, but contains separately licensed assets/dependencies and Roblox-specific code. We inspected its source without copying it.
- MacOBlox describes a host OpenGL path and experimental Zink/Vulkan, host audio forwarding, input handling, DNS adaptations, framework stubs and low-level Darling changes. It also contains binary patches, RakNet/transport patches and injected/interposed shim code. Those client-specific modifications are not acceptable in ROBLOX-LX and are explicitly excluded.
- ROBLOX-LX has no empirical evidence yet for Roblox startup, rendering, audio, input, networking, multiplayer or Hyperion under Darling. Each remains UNKNOWN. The per-API inventory is in `API_BLOCKERS.md`.

## Conclusion

A Darling process manager and independent Mach-O fixture are feasible and now implemented. Actual macOS API coverage and the Roblox client remain UNKNOWN until a Darling runtime and clean, independent tests are available. No Roblox binary or account was used. Do not claim Roblox compatibility from compile success, process start or window display alone.

## Sources

- Darling upstream project README: https://github.com/darlinghq/darling
- MacOBlox source audit (not copied): https://github.com/aubree-lat/MacOBlox
- Darling license and component licensing: https://github.com/darlinghq/darling/blob/master/LICENSE
- MacOBlox license: https://github.com/aubree-lat/MacOBlox/blob/main/LICENSE
