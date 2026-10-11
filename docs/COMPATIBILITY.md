# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Darling presence/version | PARTIAL | Executable detection and bounded `--version` probe only. |
| Darling prefix/process management | BLOCKED | Not implemented or tested. |
| Darwin API coverage | UNKNOWN | No independent macOS test executable run yet. |
| Roblox client executable architecture/frameworks | UNKNOWN | No official client inspected. |
| Official Roblox Linux support | BLOCKED | Roblox Support currently says Linux is unsupported. |
| Roblox launch, experiences, multiplayer, rendering/audio/input | UNKNOWN | Not tested; launch intentionally fails closed. |

Third-party MacOBlox reports working features, but they are not ROBLOX-LX test results and its shim technique is out of scope under the stated client-integrity rules.
