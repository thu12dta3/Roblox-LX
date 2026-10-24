# Compatibility status

| Capability | Status | Boundary |
|---|---|---|
| Linux host detection | Implemented | Read-only best-effort probes |
| Wayland/X11 session detection | Implemented | Environment-based; does not validate the compositor |
| Vulkan extension discovery | Partial | Depends on `vulkaninfo --summary` output |
| Hardware Vulkan presentation | Testable | Requires `vkcube`, active display, and a physical Vulkan device |
| Audio/input/network prerequisite discovery | Partial | Detects tools/libraries; does not test a game |
| Native Roblox Linux client | Not implemented / not verified | No compatibility claim |
| Roblox gameplay, multiplayer, or account safety | Unknown | Not tested |
| macOS/Darling/Metal compatibility | Out of scope | Removed from this repository |

A diagnostic marked PASS only applies to the capability actually exercised. Host graphics support does not prove application compatibility or performance.
