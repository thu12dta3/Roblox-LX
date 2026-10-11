# Test results

## 2026-10-11

Commands run locally:

- `PYTHONPATH=src python -m unittest discover -s tests/unit` — PASS (1 test).
- `PYTHONPATH=src python -m robloxlx.cli version` — PASS (`ROBLOX-LX 0.1.0`).
- `PYTHONPATH=src python -m robloxlx.cli doctor` — PASS; detected Garuda Linux, x86_64, kernel 7.2.9-zen1-1-zen, Wayland, NVIDIA GeForce RTX 2060 SUPER, driver 615.71.09, OpenGL 4.6.0, and Vulkan 1.4.351 on the NVIDIA device (plus llvmpipe at 1.4.354). Vulkan emitted loader warnings about optional display-property functions; device enumeration succeeded. This was not a rendering conformance test.
- `PYTHONPATH=src python -m robloxlx.cli compatibility` — PASS; reported native Linux client BLOCKED and API-translation backends OUT OF SCOPE.
- `PYTHONPATH=src python -m robloxlx.cli launch --dry-run` — PASS as a safe refusal; readiness reported BLOCKED because no official native client is available; no process started (exit 2 is expected).

GitHub Actions `Tests`, `Lint` (compile check), and `Security checks` workflows all passed on pull request #1. The checks ran for both the branch push and pull request event.

No Roblox runtime, graphics rendering, audio, input, multiplayer, or game test has been performed. Darling is no longer probed because compatibility-runtime paths are outside the native-only project scope.
