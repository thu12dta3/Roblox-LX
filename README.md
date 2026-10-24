# ROBLOX-LX

**A Mice Works project** · Linux-first compatibility research. Not affiliated with Roblox Corporation.

Copyright © 2026 Mice Works. Licensed under GNU AGPL v3; see [LICENSE](LICENSE).

ROBLOX-LX is a Linux-native project for inspecting a traditional Linux desktop environment and validating its hardware Vulkan presentation path. It intentionally excludes the macOS client route, Darling, Metal bridges, (no more MacOS) framework shims, and macOS-specific build fixtures.

## Current status

**This is a diagnostic and research foundation, not a working Roblox client.** Roblox does not provide a generally supported native Linux desktop client, and this repository does not currently implement a compatible client or guarantee that Roblox can be played on Linux.

The current code can:
- Inspect Linux distribution, kernel, architecture, graphical session, GPU/driver information, Vulkan availability, and common audio/input/network tools.
- Run a bounded Vulkan-only presentation smoke test through `vkcube` when a hardware Vulkan device and active Wayland/X11 session are available.
- Report compatibility status without claiming that host Vulkan support proves Roblox compatibility.
- Run unit tests without Roblox credentials or production game sessions.

No client is downloaded, modified, injected into, or launched by this project. It does not disable security controls, spoof anti-cheat, or alter network protocols.

## Requirements

- Linux desktop (Wayland or X11)
- Python 3.10+
- Optional diagnostics: `vulkaninfo`, `vkcube`, `nvidia-smi`, `lspci`
- A hardware Vulkan driver for `graphics-test`

No third-party Python runtime dependencies are required.

## Quick start

```sh
PYTHONPATH=src python -m robloxlx.cli doctor
PYTHONPATH=src python -m robloxlx.cli compatibility
PYTHONPATH=src python -m robloxlx.cli graphics-test --frames 3
PYTHONPATH=src python -m robloxlx.cli self-test
```

Install locally:

```sh
python -m pip install -e .
robloxlx doctor
```

On Arch Linux/Garuda, the optional local package recipe is in [packaging/arch/PKGBUILD](packaging/arch/PKGBUILD). It does not install system dependencies or configure the host.

## Commands

| Command | Purpose |
|---|---|
| `doctor` | Read-only host and dependency diagnostics |
| `compatibility` | Show the evidence-backed project status |
| `graphics-test` | Present frames with Vulkan via `vkcube` |
| `verify PATH` | Calculate a local file's SHA-256; this does not prove authenticity |
| `logs` | List ROBLOX-LX log files |
| `cleanup` | Remove only the project's dedicated temporary cache |
| `self-test` | Run unit tests from a source checkout |
| `version` | Print the installed version |

## Project layout

- `src/robloxlx/cli.py` — CLI and command dispatch
- `src/robloxlx/diagnostics.py` — read-only Linux host probes
- `src/robloxlx/graphics/vulkan.py` — bounded hardware Vulkan smoke test
- `tests/unit/` — unit tests
- `docs/` — architecture, compatibility, development, security, and roadmap

## Development and tests

```sh
PYTHONPATH=src python -m unittest discover -s tests/unit -v
PYTHONPATH=src python -m robloxlx.cli version
python -m compileall -q src tests
```

CI runs unit tests and static checks on Ubuntu with Python 3.12. A passing unit suite does not prove Vulkan works on every GPU or that Roblox is compatible. Hardware-dependent checks must be run on the target Linux machine and reported separately.

See [Architecture](docs/ARCHITECTURE.md), [Compatibility](docs/COMPATIBILITY.md), [Security](docs/SECURITY.md), [Development](docs/DEVELOPMENT.md), and [Roadmap](docs/ROADMAP.md).

## About Mice Works

Mice Works is the project brand behind ROBLOX-LX. The repository is currently hosted under the GitHub account `thu12dta3`; this branding statement does not itself transfer the repository to a GitHub organization.

## License

ROBLOX-LX is licensed under GNU AGPL v3. See [LICENSE](LICENSE). Third-party notices remain applicable to their respective components.
