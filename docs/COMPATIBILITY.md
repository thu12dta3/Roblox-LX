# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Host Vulkan WSI extensions | PASS / UNKNOWN | `doctor` reads `VK_KHR_surface` and the active Wayland/XCB instance extension from `vulkaninfo --summary`; this does not test Darling or Metal translation. |
| Darling discovery and process lifecycle | IMPLEMENTED | Python standard library; argv safety, path mapping, process exit, log permissions, and missing-runtime unit coverage. |
| Darling host kernel prerequisites | PARTIAL | `doctor` checks matching kernel build headers and reports whether `darling-mach` is loaded, available, absent, or unknown; it never loads the module. |
| Independent x86_64 Mach-O fixture build | PASS | Built with host `clang` 23.1.1 and `ld64.lld` 23.1.1; verified `cffaedfe` Mach-O 64-bit header. |
| Independent Mach-O fixture build and app preflight | PASS | Local executable is built and validated as x86_64 Mach-O; `.app` main executable is resolved from `Info.plist`; ELF and wrong architecture are rejected. |
| Independent Mach-O execution under Darling | BLOCKED | `darling` executable is absent on the development host. `robloxlx darling-test` reports the missing runtime without starting a process. |
| Graphics/audio/input/network host prerequisites | PARTIAL | Read-only library and utility discovery only; no device IO was exercised through Darling. |
| macOS Roblox client under Darling | UNKNOWN | No Roblox executable downloaded or run; no compatibility claim. |
| Gameplay and multiplayer | UNKNOWN | No session or account test was run. |
| Client patches, anti-cheat modifications, protocol changes | BLOCKED | Prohibited by repository policy and absent from this implementation. |
| Android/mobile client, macOS/Windows VM | OUT OF SCOPE | Excluded by user requirement. |

Roblox remains NOT TESTED. See [API blockers](API_BLOCKERS.md) for precise observations and unknowns.
