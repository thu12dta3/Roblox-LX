# Feasibility research — 2026-10-11

This is a documentary audit, not a runtime test. Roblox client binaries were not obtained or inspected.

## Findings

| Question | Finding | Status |
|---|---|---|
| Is Roblox desktop supported on Linux? | Roblox Support says Linux is not supported. | SUPPORTED (as a statement in current support docs) |
| Does Darling run macOS binaries? | Darling describes a Mach-O loader and userspace Darwin/Mach interfaces, with reimplemented frameworks. | SUPPORTED |
| Is Darling GUI support complete? | Darling says GUI app support is in active development; its README describes an initial Metal backend using Vulkan translation. This is not evidence of complete app compatibility. | PARTIAL |
| Is x86_64 available? | Darling project material describes x86_64 support; platform support does not guarantee a specific app runs. | PARTIAL |
| Is a Roblox macOS x86_64 binary currently usable? | Not inspected in this project. Roblox's supported OS statement alone does not establish current binary architecture or downloadable deployment. | UNKNOWN |
| Which exact frameworks/APIs does the current client require? | Not measured against an official unmodified bundle here. | UNKNOWN |
| Graphics API requirements? | Roblox documentation exposes OpenGL, Metal, and Vulkan graphics modes at engine/API level; this does not establish which backend a particular macOS client selects. | UNKNOWN for client selection |
| MacOBlox state? | Its public README claims Linux execution through Darling, and describes injected compatibility libraries for mouse, sound, OpenGL, and network, plus fixes. It reports startup verification on NVIDIA OpenGL 4.1; heavier gameplay remains explicitly untested/experimental. This is a third-party claim, not independently reproduced. | PARTIAL, claims not verified here |
| Can ROBLOX-LX reuse MacOBlox? | The source repository identifies MIT licensing, but its described client shims/injection conflict with this project's user-mandated no-client-modification policy. No code copied. | BLOCKED under project policy for that technique |
| Can Darling/Wine source be bundled under this exact proprietary notice? | Darling is GPL-3.0 and Wine uses LGPL-family licensing. Combining/distributing code may impose obligations incompatible with the requested exact proprietary-only treatment; no code was copied. External use/integration needs component-specific legal review. | UNKNOWN pending legal review |
| Is Wine a direct macOS backend? | No. Wine implements Windows APIs and is a potential environment for the Windows client, not a translation layer for a macOS binary. The Windows-client route would need separate current anti-cheat and platform-policy review; this project will not bypass those controls. | BLOCKED as an unassessed alternate route |
| Darling bottlenecks? | Complete AppKit/graphics/API coverage and app-specific framework use have not been analyzed from a real client binary. Roblox official non-support is also a platform-policy limitation. | UNKNOWN / BLOCKED |

## Engineering conclusion

Execution through Darling appears technically plausible in the broader ecosystem: MacOBlox reports successful startup and selected gameplay functionality. However, that project's own description says it adds compatibility libraries to the game. ROBLOX-LX's pasted requirements prohibit modifying the client or inserting code. Under those constraints, no viable launch route has been established. This is a real policy/technical blocker, not proof that all clean external compatibility implementations are impossible.

The immediate permissible work is host diagnostics, independent Darwin API tests, and an external Darling process manager. A future test should use a simple authorized macOS executable first. Re-evaluate any Roblox path only if a transparent out-of-process implementation is demonstrated and its use is authorized; do not reproduce prohibited shims or patching.

## Sources

- [Roblox Support: Computer Hardware & Operating System Requirements](https://en.help.roblox.com/hc/en-us/articles/203312800-Computer-Hardware-Operating-System-Requirements)
- [Darling project README](https://github.com/darlinghq/darling)
- [MacOBlox project README](https://github.com/aubree-lat/MacOBlox)
- [Roblox Creator Hub GraphicsMode reference](https://create.roblox.com/docs/reference/engine/enums/GraphicsMode)
- [Wine source repository](https://gitlab.winehq.org/wine/wine)
- [WineHQ: About Wine](https://www.winehq.org/about)
- [Wine source mirror license notice](https://github.com/wine-mirror/wine/blob/master/LICENSE)

Pages accessed 2026-10-11. The MacOBlox and Darling statements are upstream project claims; ROBLOX-LX did not independently test them.
