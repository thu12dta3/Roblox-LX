# ROBLOX-LX

**Bannaman6655 Productions** — private project seeking a native Linux Roblox client. ROBLOX-LX is not affiliated with Roblox Corporation.

## Purpose and current state

The goal is to play Roblox normally through a **native Linux desktop client**, without a virtual machine, emulator, or operating-system API translation layer. The current release is only an early diagnostic CLI foundation; it does not install or launch Roblox. Roblox's official requirements currently list Linux as unsupported. Until Roblox provides a native Linux client or an official interface that permits one, native Linux execution is BLOCKED. See [feasibility](docs/FEASIBILITY.md) and [risks](docs/RISKS.md).

## Implemented

- `robloxlx doctor`: read-only host and graphics-tool probes.
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
| Native Linux Roblox client | BLOCKED | Roblox Support lists Linux as unsupported; no official Linux client is available to this project. |
| VM, emulator, or OS API translation | OUT OF SCOPE | Explicitly excluded by the project goal. |
| Roblox launch | BLOCKED | Requires an official native Linux client or official Roblox-supported interface. |
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
