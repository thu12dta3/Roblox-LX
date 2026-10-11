# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Darling discovery and process lifecycle | IMPLEMENTED | Python standard library; argv safety, path mapping, process exit, log permissions, and missing-runtime unit coverage. |
| Independent x86_64 Mach-O fixture build | PASS | Built with host `clang` 23.1.1 and `ld64.lld` 23.1.1; verified `cffaedfe` Mach-O 64-bit header. |
| Independent Mach-O execution under Darling | BLOCKED | `darling` executable is absent on the development host. The integration test is present and skips for this reason. |
| Graphics/audio/input/network host prerequisites | PARTIAL | Read-only library and utility discovery only; no device IO was exercised through Darling. |
| macOS Roblox client under Darling | UNKNOWN | No Roblox executable downloaded or run; no compatibility claim. |
| Gameplay and multiplayer | UNKNOWN | No session or account test was run. |
| Client patches, anti-cheat modifications, protocol changes | BLOCKED | Prohibited by repository policy and absent from this implementation. |
| Android/mobile client, macOS/Windows VM | OUT OF SCOPE | Excluded by user requirement. |

Roblox remains NOT TESTED. See [API blockers](API_BLOCKERS.md) for precise observations and unknowns.
