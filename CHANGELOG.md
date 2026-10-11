# Changelog

## 0.1.0 — 2026-10-11

- Initial private foundation: read-only diagnostic CLI, cautious integrity measurement, compatibility status, and local unit coverage.
- No Roblox client installation or execution support is implemented.
- Clarified the compatibility direction: translate Windows desktop APIs through Wine only; exclude VMs, macOS client paths, and mobile clients.
- Added Wine detection and safe command construction; an isolated minimal PE startup check passed. Roblox remains untested and blocked by Hyperion's stated Wine incompatibility.
