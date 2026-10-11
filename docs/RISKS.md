# Risks

- Roblox officially does not support Linux. Third-party compatibility is unsupported by Roblox and account-risk-free operation cannot be promised.
- MacOBlox publicly describes injected shims and client-side fixes. Reproducing those methods would violate ROBLOX-LX's stated integrity rules; this repository does not implement them.
- Darling's active GUI/framework implementation does not prove complete compatibility with this client.
- No client binary, login, production account, or game server was used in this work.
- A local SHA-256 digest has no authenticity meaning without a trusted official expected digest or signature verification key/chain.
- Darling (GPL-3.0) and Wine (LGPL) licenses require component-level review before source integration or redistribution; no third-party source is incorporated.
- Host diagnostic output can reveal device/system details if shared; review logs before publication.

Risk reduction: keep the official executable unmodified, never handle passwords/tokens, keep logs local, and test compatibility first with independently authorized macOS binaries.
