# Risks

- Roblox does not provide a generally supported native Linux desktop client; this repository does not currently implement a working client.
- A passing host Vulkan smoke test proves only that the tested Linux Vulkan presentation path works. It does not prove Roblox compatibility, gameplay, multiplayer, or performance.
- Third-party compatibility work is unsupported by Roblox, and account-risk-free operation cannot be promised for future approaches.
- Client modification, code injection, anti-cheat evasion, and protocol spoofing are prohibited by project policy.
- No Roblox credentials, account sessions, or production game servers are used by the diagnostic suite.
- A local SHA-256 digest does not establish authenticity without a trusted publisher signature or digest baseline.
- Host diagnostics can expose device and system details if shared; review output before publishing logs.
- Hardware-dependent Vulkan results vary by GPU, driver, compositor, and session type.

Risk reduction: keep the current tooling read-only, make claims only from reproducible evidence, and validate any future Linux compatibility approach against explicit security and licensing constraints.
