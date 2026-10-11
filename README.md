# ROBLOX-LX

**Bannaman6655 Productions** — private Linux desktop compatibility project. ROBLOX-LX is not affiliated with Roblox Corporation.

## Purpose and current state

The goal is to run the official **Windows desktop client** on Linux by translating the APIs it calls through Wine, without booting or emulating a Windows/macOS operating system. Mac clients, mobile/tablet versions, and VMs are out of scope. The current release is only an early diagnostic CLI foundation; it does not install or launch Roblox. Roblox lists Linux as unsupported, and a Roblox staff statement says Hyperion with all security features enabled does not work under Wine. We will not bypass or disable it, so gameplay remains BLOCKED unless Roblox restores official Wine support or provides a compliant path. See [feasibility](docs/FEASIBILITY.md) and [risks](docs/RISKS.md).

## Implemented

- `robloxlx doctor`: read-only host, graphics-tool, and Wine API-translator probes.
- Wine runtime detection and safe argument construction for an existing local Windows program (no execution yet).
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
| Roblox Windows desktop client under Wine API translation | BLOCKED | Roblox staff says Hyperion with all features enabled does not work on Wine; no bypass is implemented. |
| Full Windows/macOS OS, VM, emulator, Mac/mobile client | OUT OF SCOPE | Explicitly excluded. |
| Roblox launch | BLOCKED | No currently validated path that keeps Hyperion intact. |
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
