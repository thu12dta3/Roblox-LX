# Feasibility research — 2026-10-11

This is a documentary audit, not a runtime test. No Roblox binaries were obtained or inspected. The project requirement is native Linux execution: no VM, emulator, or operating-system API translation.

## Findings

| Question | Finding | Status |
|---|---|---|
| Does Roblox officially support Linux desktop? | Roblox Support lists Linux as unsupported; PC requirements list Windows 10/11 and macOS. | BLOCKED |
| Is a native Linux Roblox desktop client available to this project? | No official Linux client is documented by Roblox Support. | BLOCKED |
| Would Darling meet the clarified goal? | No. Darling runs macOS binaries by translating/reimplementing Darwin and macOS APIs on Linux. That is a compatibility translation layer. | OUT OF SCOPE |
| Would Wine meet the clarified goal? | No. Wine translates Windows APIs for Linux. | OUT OF SCOPE |
| Would a virtual machine/emulator meet the clarified goal? | No, explicitly excluded by the user. | OUT OF SCOPE |
| Can ROBLOX-LX build a native client from the current public interfaces? | No supported native client or official Linux client-development interface has been identified. The Roblox client is proprietary and its source is not in this repository. | BLOCKED pending Roblox |
| Can Darling or Wine source be integrated? | Irrelevant to the clarified native-only product goal; no code was copied. License notices are retained for research awareness only. | OUT OF SCOPE |
| Has Roblox been launched or tested? | No. | NOT TESTED |

## Conclusion

The requested result cannot currently be implemented within the stated constraints. Roblox's official requirements say Linux is unsupported, and no official native Linux client is available here. Making an existing Windows or macOS client run on Linux requires an API-translation layer or VM/emulator, which the user explicitly ruled out. A launcher, graphics driver, or diagnostics tool cannot replace Roblox's proprietary client.

The product goal is therefore BLOCKED by an external dependency: Roblox must release a native Linux client or an official interface and authorization for a native client. Until then, ROBLOX-LX should not pursue Darling, Wine, emulation, or compatibility shims as substitutes. Maintain only the diagnostic scaffold and report the blocker clearly.

## Sources

- [Roblox Support: Computer Hardware & Operating System Requirements](https://en.help.roblox.com/hc/en-us/articles/203312800-Computer-Hardware-Operating-System-Requirements)
- [Darling project README](https://github.com/darlinghq/darling) — documents macOS API translation on Linux; reviewed only to assess and exclude it.
- [WineHQ: About Wine](https://www.winehq.org/about) — describes Windows API translation; reviewed only to assess and exclude it.
- [MacOBlox project README](https://github.com/aubree-lat/MacOBlox) — third-party Darling-based path; not used or tested here.

Sources accessed 2026-10-11. Third-party project claims were not independently reproduced.
