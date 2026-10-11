# ROBLOX-LX

**Bannaman6655 Productions** — private, proprietary Linux compatibility research project. ROBLOX-LX is not affiliated with Roblox Corporation.

## Purpose and current state

This project investigates whether the official desktop client can run on Linux through a transparent compatibility layer. The current release is an early diagnostic CLI foundation. It does not install, modify, or launch Roblox. Roblox's support documentation currently says Linux is unsupported. A third-party Darling project, MacOBlox, publicly reports running the macOS client, but its described implementation includes compatibility shims loaded into the game. That path is outside this project's stated no-client-modification policy. See [feasibility](docs/FEASIBILITY.md) and [risks](docs/RISKS.md).

## Implemented

- `robloxlx doctor`: read-only host, graphics-tool, NVIDIA and Darling probes.
- `robloxlx verify`: optional SHA-256 measurement for a user-configured local file; no official trust baseline is bundled.
- `robloxlx compatibility`: reports current known limitations.
- `robloxlx launch --dry-run`: reports readiness and never starts a process.
- `robloxlx launch`: safely reports BLOCKED while there is no validated backend.
- `robloxlx logs`, `self-test`, `cleanup`, and `version`.

## Development use

Requires Python 3.10+. From a checkout:

```sh
python -m pip install -e .
robloxlx doctor
robloxlx compatibility
robloxlx self-test
```

Optional host probes are `nvidia-smi`, `lspci`, `glxinfo`, and `vulkaninfo`. Missing probes are reported as UNKNOWN. No system packages are installed or global settings changed.

## Compatibility status

| Capability | Status | Evidence |
|---|---|---|
| Linux support by Roblox | BLOCKED | Roblox Support lists Linux as unsupported. |
| Darling runtime detection | PARTIAL | CLI can detect the command; no backend lifecycle support yet. |
| Roblox macOS client architecture/framework requirements | UNKNOWN | No official app bundle has been inspected in this project. |
| Roblox launch using ROBLOX-LX policy | BLOCKED | No no-modification backend validated; no real client test performed. |
| Games, rendering, audio, input, multiplayer | UNKNOWN | No real-client or game test performed. |

Never interpret a local hash as proof that a binary is official. Do not supply account passwords to ROBLOX-LX. Do not disable or bypass anti-cheat mechanisms.

## Documents

- [Architecture](docs/ARCHITECTURE.md)
- [Baseline audit](docs/BASELINE.md)
- [Feasibility research](docs/FEASIBILITY.md)
- [Compatibility matrix](docs/COMPATIBILITY.md)
- [Security](docs/SECURITY.md)
- [Risks](docs/RISKS.md)
- [Roadmap](docs/ROADMAP.md)
- [Test results](docs/TEST_RESULTS.md)
- [Development](docs/DEVELOPMENT.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## License

The exact proprietary notice in `LICENSE` applies to materials owned by Bannaman6655 Productions. It does not change third-party licenses or rights. No third-party source code is bundled in this initial implementation.
