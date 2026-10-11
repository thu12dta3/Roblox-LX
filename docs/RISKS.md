# Risks

- Roblox officially does not support Linux. Third-party compatibility is unsupported by Roblox and account-risk-free operation cannot be promised.
- Roblox does not currently support a native Linux client. No amount of local launcher or graphics work can substitute for its proprietary client.
- Darling, Wine, VMs, and emulators do not meet the clarified native-only requirement and are excluded from the implementation roadmap.
- Third-party MacOBlox compatibility claims do not constitute native Linux execution or ROBLOX-LX test results.
- No client binary, login, production account, or game server was used in this work.
- A local SHA-256 digest has no authenticity meaning without a trusted official expected digest or signature verification key/chain.
- Darling (GPL-3.0) and Wine (LGPL) licenses require component-level review before source integration or redistribution; no third-party source is incorporated.
- Host diagnostic output can reveal device/system details if shared; review logs before publication.

Risk reduction: keep the official executable unmodified, never handle passwords/tokens, keep logs local, and test compatibility first with independently authorized macOS binaries.
