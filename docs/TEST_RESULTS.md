# Test results

## 2026-10-11

Commands run locally:

- `PYTHONPATH=src python -m unittest discover -s tests/unit` — PASS (4 tests).
- `PYTHONPATH=src python -m robloxlx.cli version` — PASS (`ROBLOX-LX 0.1.0`).
- `PYTHONPATH=src python -m robloxlx.cli doctor` — PASS; detected Garuda Linux, x86_64, kernel 7.2.9-zen1-1-zen, Wayland, NVIDIA GeForce RTX 2060 SUPER, driver 615.71.09, OpenGL 4.6.0, Vulkan 1.4.351 on the NVIDIA device (plus llvmpipe at 1.4.354), and Wine 11.19. Vulkan emitted loader warnings about optional display-property functions; device enumeration succeeded. This was not a rendering conformance test.
- `PYTHONPATH=src python -m robloxlx.cli compatibility` — PASS; reported Wine API translation as the permitted direction, Hyperion/Wine as BLOCKED, and macOS/mobile/VM paths OUT OF SCOPE.
- `PYTHONPATH=src python -m robloxlx.cli launch --dry-run` — PASS as a safe refusal; Wine/Hyperion is not validated; no process started (exit 2 is expected).

GitHub Actions `Tests`, `Lint` (compile check), and `Security checks` workflows all passed on pull request #1. The checks ran for both the branch push and pull request event.

Additional independent runtime check:

- Compiled a trivial x86_64 Windows PE entry-point program with the already installed Clang/LLD and ran it using Wine 11.19 under a temporary `WINEPREFIX` — PASS (exit 0). Wine/Mesa printed EGL device warnings during prefix initialization; the smoke program completed. This checks basic PE startup only, not Windows API coverage, rendering, or application compatibility.
- Four unit tests cover missing Wine detection, argument-vector safety, and invalid/missing executable paths.

No Roblox binary, account, or game was used. No Roblox runtime, Roblox gameplay, graphics rendering, audio, input, or multiplayer test has been performed.
