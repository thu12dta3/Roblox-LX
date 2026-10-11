# Risks

- Roblox officially does not support Linux. Third-party compatibility is unsupported by Roblox and account-risk-free operation cannot be promised.
- Darling's GUI, graphics, audio and API coverage for the Roblox macOS client is unknown until tested with independent programs.
- The installed Darling runtime is absent on the current development host, so Mach-O execution is not yet confirmed.
- A client process starting or window appearing would not establish gameplay, networking or multiplayer functionality.
- Client modification, code injection, anti-cheat evasion and protocol spoofing are prohibited by project rules.
- Android/mobile clients and full OS virtual machines are excluded by the user.
- No client binary, login, production account, or game server was used in this work.
- A local SHA-256 digest has no authenticity meaning without a trusted official expected digest or signature verification key/chain.
- Darling is GPL-3.0 with potentially distinct subcomponent licenses; it remains an external runtime and no source is incorporated.
- Host diagnostic output can reveal device/system details if shared; review logs before publication.

Risk reduction: keep the official executable unmodified, never handle passwords/tokens, keep logs local, and test compatibility first with independently authorized macOS binaries.
