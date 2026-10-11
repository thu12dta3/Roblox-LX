# Test results

## 2026-10-11 (Darling backend work)

Recorded after executing the commands in this section:

- `python -m unittest discover -s tests/unit` — first attempt without the source tree installed/importable failed with three `ModuleNotFoundError: robloxlx` collection errors. The checkout test command `PYTHONPATH=src python -m unittest discover -s tests/unit` then passed all 5 runnable tests; 1 integration test skipped because Darling is absent.
- `PYTHONPATH=src python -m robloxlx.cli doctor` — PASS; Garuda Linux, x86_64, kernel 7.2.9-zen1-1-zen, Wayland, RTX 2060 SUPER, driver 615.71.09; OpenGL 4.6.0, Vulkan 1.4.351 (NVIDIA; llvmpipe also reported at 1.4.354); Darling NOT FOUND. OpenGL/EGL/Vulkan, PipeWire/PulseAudio, X11/XInput2/Wayland host libraries found; `pw-cat`, `pacat`, `pactl`, `libinput`, `getent`, `resolvectl`, and graphics probes detected. This is discovery, not an I/O test.
- `PYTHONPATH=src python -m robloxlx.cli compatibility` — PASS; Darling NOT FOUND and Roblox/gameplay UNKNOWN.
- `PYTHONPATH=src python -m robloxlx.cli launch --dry-run` — PASS as safe refusal (exit 2; target path required).
- `PYTHONPATH=src python -m robloxlx.cli launch --program /bin/true` — PASS as safe refusal (exit 2; Darling NOT FOUND, no process started).
- Process manager fake-runtime test — PASS; validates argv mapping, output capture, exit status and mode-0600 log.
- `PYTHONPATH=src python -m compileall -q src tests/unit` — PASS.
- `git diff --check` — PASS.
- Arch packaging metadata: `(cd packaging/arch && makepkg --printsrcinfo)` and `bash -n PKGBUILD` — PASS; package installation/build was not run.
- Standalone Mach-O fixture — `clang -target x86_64-apple-macos10.15` and `ld64.lld` both succeeded; `file` reported Mach-O 64-bit x86_64 executable and magic `cffaedfe`.
- Actual Mach-O execution through Darling — BLOCKED because `darling` is not installed. The integration test is present and skips unless Darling, Clang and ld64.lld are available.
- Roblox executable, account, credentials, client rendering/audio/input/network/gameplay — NOT TESTED.

Earlier Wine-only tests and runtime experiments do not establish Darling or Roblox compatibility.
