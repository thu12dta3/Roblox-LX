# Test results

## 2026-10-11 (Darling runtime installation check)

- `pacman -Q darling-cli-release-local` — PASS; local package version `20260609-1` is installed.
- `darling --version` — PASS as a launcher-only check; initialized `~/.darling` and printed `darling HEAD @ e947f0d5`. This does not prove that the Darwin runtime starts.
- `PYTHONPATH=src python -m robloxlx.cli darling-test` — BLOCKED; local Mach-O fixture compiled, but Darling returned exit 1 before executing it: `Failed to start darlingserver` / `Cannot open mnt namespace file: No such file or directory`.
- Package inspection found that the locally assembled `20260609-1` package omitted the official `darlingserver` helper. A corrected local `20260609-2` package was built; payload SHA-256 is `cfbdcc102ed06cc3ca7f60b683c510fc15c9d681693ebcdea6ee2a2de1c6dc47`. It has not been installed because sudo requires a password and the integrated terminal did not open. The integration unit test skips with this exact missing-helper condition.
- `PYTHONPATH=src python -m unittest discover -s tests/unit` — PASS; 19 tests ran, 1 integration test skipped because `/usr/bin/darlingserver` is absent.
- `PYTHONPATH=src python -m robloxlx.cli doctor` — PASS; Garuda Linux, x86_64, Wayland, NVIDIA GeForce RTX 2060 SUPER, Vulkan 1.4.351/1.4.354 and Vulkan Wayland WSI extensions detected. Darling is reported `INCOMPLETE (darlingserver NOT FOUND; version not queried)`. Audio, input and network utilities are present; this checks host dependencies only.
- `PYTHONPATH=src python -m robloxlx.cli graphics-test --frames 3` — PASS; three Vulkan Wayland swapchain frames on the NVIDIA RTX 2060 SUPER; output confirms OpenGL was not used. This is host Vulkan only, not Metal through Darling.
- `PYTHONPATH=src python -m robloxlx.cli self-test` — PASS; 19 tests ran, 1 integration test skipped for the missing Darling helper.
- Roblox executable, client graphics/audio/input/network, account and gameplay — NOT TESTED.

## 2026-10-11 (Darling backend baseline before runtime installation)

Recorded after executing the commands in this section:

- `python -m unittest discover -s tests/unit` — first attempt without the source tree importable failed with three `ModuleNotFoundError: robloxlx` collection errors. Latest `PYTHONPATH=src python -m unittest discover -s tests/unit` passed 18 tests; 1 integration test skipped because Darling is absent. A test confirms runtime discovery never executes the Darling launcher; the app-bundle traversal case confirms an `Info.plist` executable path cannot escape its `.app` directory.
- `PYTHONPATH=src python -m robloxlx.cli doctor` — PASS; Garuda Linux, x86_64, kernel 7.2.9-zen1-1-zen, Wayland, RTX 2060 SUPER, driver 615.71.09; Vulkan 1.4.351 on NVIDIA and 1.4.354 on llvmpipe; `VK_KHR_surface` and `VK_KHR_wayland_surface` FOUND; Darling NOT FOUND. Vulkan, PipeWire/PulseAudio, X11/XInput2/Wayland host libraries found; `vkcube`, `vulkaninfo`, `pw-cat`, `pacat`, `pactl`, `libinput`, `getent`, and `resolvectl` detected. Diagnostics do not probe OpenGL.
- Invoking `--help` on the locally extracted official release launcher stopped before starting Darling and reported that the host launcher requires setuid root for namespace/mount setup; the package remains uninstalled.
- `PYTHONPATH=src python -m robloxlx.cli graphics-test --frames 3` — PASS; `vkcube` presented three Wayland swapchain frames on NVIDIA GeForce RTX 2060 SUPER (`PHYSICAL_DEVICE_TYPE_DISCRETE_GPU`). It used Vulkan directly and did not use OpenGL. This tests host presentation only, not Darling's macOS Metal window path.
- `PYTHONPATH=src python -m robloxlx.cli compatibility` — PASS; Darling NOT FOUND and Roblox/gameplay UNKNOWN.
- `PYTHONPATH=src python -m robloxlx.cli launch --dry-run` — PASS as safe refusal (exit 2; target path required).
- `PYTHONPATH=src python -m robloxlx.cli launch --program /bin/true --dry-run` — PASS as safe refusal (exit 1; ELF rejected before Darling discovery).
- `PYTHONPATH=src python -m robloxlx.cli darling-test` — BLOCKED as expected (exit 2; Darling NOT FOUND, no process started).
- Process manager fake-runtime test — PASS; validates argv mapping, output capture, exit status and mode-0600 log.
- Mach-O/App bundle preflight — PASS; builds a real local x86_64 Mach-O fixture, recognizes its architecture, resolves an `.app` main executable from `Info.plist`, and rejects ELF/wrong-architecture files before launch. `darling-test` is the repeatable independent runtime test when Darling is present.
- Vulkan selection and software-device rejection unit tests — PASS.
- `PYTHONPATH=src python -m compileall -q src tests/unit` — PASS.
- `git diff --check` — PASS.
- GitHub Actions on follow-up PR #3 after fixes — Tests PASS, Lint PASS, Security checks PASS. The first CI run exposed a frame-count validation test ordering bug, which was fixed before the passing run. The earlier Security checks failure was fixed by adding narrow explanations to shell-free subprocess calls.
- Arch packaging metadata: `(cd packaging/arch && makepkg --printsrcinfo)` and `bash -n PKGBUILD` — PASS; package installation/build was not run.
- Standalone Mach-O fixture — `clang -target x86_64-apple-macos10.15` and `ld64.lld` both succeeded; `file` reported Mach-O 64-bit x86_64 executable and magic `cffaedfe`.
- Actual Mach-O execution through Darling — BLOCKED because `darling` is not installed. The integration test is present and skips unless Darling, Clang and ld64.lld are available.
- Roblox executable, account, credentials, client rendering/audio/input/network/gameplay — NOT TESTED.

Earlier Wine-only tests and runtime experiments do not establish Darling or Roblox compatibility.
