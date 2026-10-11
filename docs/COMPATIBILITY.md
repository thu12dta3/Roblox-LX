# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Native Roblox client for Linux | BLOCKED | Roblox Support currently says Linux is unsupported; no official Linux build is available to this project. |
| VM, emulator, or API translation | OUT OF SCOPE | Excluded by the user's clarified requirement. |
| Roblox launch, experiences, multiplayer, rendering/audio/input | UNKNOWN | Not tested; launch intentionally fails closed. |

Third-party MacOBlox reports working features through Darling, but that is a translated macOS environment and does not meet ROBLOX-LX's native-only goal. Those reports are not ROBLOX-LX test results.
