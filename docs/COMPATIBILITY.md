# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Host Vulkan WSI extensions | PASS / UNKNOWN | `doctor` reads `VK_KHR_surface` and the active Wayland/XCB instance extension from `vulkaninfo --summary`; this does not test Darling or Metal translation. |
| Darling discovery and process lifecycle | IMPLEMENTED | Python standard library; argv safety, path mapping, process exit, log permissions, and missing-runtime unit coverage. |
| Darling runtime discovery | IMPLEMENTED | `doctor` only checks PATH and does not start Darling or initialize its default prefix. |
| Independent x86_64 Mach-O fixture build | PASS | Built with host `clang` 23.1.1 and `ld64.lld` 23.1.1; verified `cffaedfe` Mach-O 64-bit header. |
| Independent Mach-O fixture build and app preflight | PASS | Local executable is built and validated as x86_64 Mach-O; `.app` main executable is resolved from `Info.plist`; ELF and wrong architecture are rejected. |
| Independent Mach-O execution under Darling | PASS | Installed Darling executed real libSystem write/exit calls and returned the expected marker with status 0. |
| Darwin DNS and TCP loopback | PASS with limitation | `network-test` resolved localhost and transferred TCP bytes with accept address output buffers. `accept(fd, NULL, NULL)` failed; external networking and Roblox are untested. |
| Darling Metal device/buffer probe | PASS with separate patched framework | Real GPU fill/copy, bytes verified, clean exit on RTX 2060 SUPER with one physical ICD. Installed system framework remains original. |
| Independent macOS Vulkan WSI | PASS on tested host | Real Wayland and X11/XWayland surface/swapchain, 30 presentations of Metal-filled pixels. See VULKAN_WINDOW.md. |
| NSWindow/NSView/CAMetalLayer Vulkan integration | UNKNOWN / pending | Independent fixture uses native SDL, not the public window/layer APIs. Upstream QuartzCore path still uses OpenGL. |
| Graphics/audio/input/network host prerequisites | PARTIAL | Host dependencies detected; audio and input through Darling remain untested. |
| macOS Roblox client under Darling | UNKNOWN | No Roblox executable downloaded or run; no compatibility claim. |
| Gameplay and multiplayer | UNKNOWN | No session or account test was run. |
| Client patches, anti-cheat modifications, protocol changes | BLOCKED | Prohibited by repository policy and absent from this implementation. |
| Android/mobile client, macOS/Windows VM | OUT OF SCOPE | Excluded by user requirement. |

Roblox remains NOT TESTED. See [API blockers](API_BLOCKERS.md) for precise observations and unknowns.
