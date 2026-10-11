# Compatibility

| Component/capability | Status | Evidence / boundary |
|---|---|---|
| Linux host detection | SUPPORTED | Implemented read-only Python probes. |
| Graphics utility detection | PARTIAL | Detects utility availability and samples output; not a rendering test. |
| Windows API translation through Wine | PARTIAL | Wine 11.19 is detected; a trivial x86_64 PE startup smoke passed in an isolated temporary prefix. This is not an API-coverage or Roblox test. |
| Hyperion on Wine | BLOCKED | Roblox staff says full-featured Hyperion does not work on Wine. No bypass is permitted. |
| macOS client/Darling | OUT OF SCOPE | Explicitly excluded by the user. |
| Mobile/tablet client or VM | OUT OF SCOPE | Explicitly excluded by the user. |
| Roblox launch, experiences, multiplayer, rendering/audio/input | UNKNOWN | Not tested; launch intentionally fails closed. |

Roblox itself remains NOT TESTED. The Wine adapter is limited to discovery and command construction; no Wine backend lifecycle or Roblox launch path exists yet.
