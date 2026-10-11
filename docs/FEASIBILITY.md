# Feasibility research — 2026-10-11

Documentary audit only; no Roblox binary or account was used. Agreed project scope: official Windows desktop client plus user-space Windows API translation through Wine; no Windows/macOS guest operating system, VM, mobile/tablet client, or macOS client. Roblox files remain unmodified and anti-cheat is not bypassed.

## Findings

| Question | Finding | Status |
|---|---|---|
| Does Roblox officially support Linux? | Current Roblox Support requirements list Linux as unsupported. | BLOCKED (official support) |
| Can desktop Windows APIs be translated without a Windows VM? | Wine describes itself as translating Windows API calls to POSIX; it does not boot a Windows guest OS. | SUPPORTED (general capability) |
| Is Wine a candidate layer within the clarified scope? | Yes, as an external Windows API compatibility runtime; it must not be confused with full Windows emulation or a VM. | IN SCOPE, not integrated yet |
| Does Roblox's Windows client work with Hyperion on Wine today? | Roblox staff member Bitdancer stated Hyperion with all features enabled does not work on Wine, explaining that unsupported undocumented features are missing. | BLOCKED (per staff statement) |
| Can ROBLOX-LX disable those Hyperion checks or fake support? | No. That violates the project's explicit safety rules. | BLOCKED / PROHIBITED |
| Is there a Roblox-issued Linux client? | Not documented in Roblox's current PC system requirements. | BLOCKED |
| Are macOS client, mobile/tablet client, Darling, or VM routes allowed? | No, explicitly excluded by the user. | OUT OF SCOPE |
| Has the Roblox client been launched or tested? | No. Wine 11.19 is installed; only a locally compiled minimal x86_64 PE smoke program was run in a temporary Wine prefix. No Roblox files or account were touched. | NOT TESTED |

## Engineering conclusion

The clarified plan can use Windows API translation through Wine without a Windows VM. Wine 11.19 is present on the target host, and a locally compiled, trivial x86_64 PE program completed under Wine using a temporary prefix. This confirms only basic PE startup; it says nothing about Roblox. The practical blocker remains Hyperion: Roblox staff says full-featured Hyperion does not work on Wine. The project can implement a Wine process/runtime manager and test harmless Windows desktop programs. It cannot reach normal Roblox gameplay unless Roblox makes Hyperion compatible with Wine or provides another supported path. Do not patch Roblox, disable Hyperion, or claim a successful launch before evidence exists.

## Sources

- [Roblox Support: Computer Hardware & Operating System Requirements](https://en.help.roblox.com/hc/en-us/articles/203312800-Computer-Hardware-Operating-System-Requirements)
- [Roblox Developer Forum: staff statement on Hyperion and Wine](https://devforum.roblox.com/t/roblox-on-linux-everything-summarized-in-1-post-updated/3236696/42)
- [WineHQ: About Wine](https://www.winehq.org/about)
- [Darling project README](https://github.com/darlinghq/darling) — excluded; this is a macOS compatibility layer.
- [MacOBlox project README](https://github.com/aubree-lat/MacOBlox) — excluded; it uses the macOS client and Darling.

Sources accessed 2026-10-11. The staff statement is Roblox's published explanation; ROBLOX-LX did not independently test Hyperion.
