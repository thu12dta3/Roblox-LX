"""Command line interface for ROBLOX-LX."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import unittest
from pathlib import Path

from robloxlx import __version__
from robloxlx.compatibility.darling import (
    build_darling_command, detect_darling, resolve_macos_executable, run_darling,
    test_darling_runtime, test_metal_runtime, test_network_runtime, test_window_runtime,
)
from robloxlx.diagnostics import collect_diagnostics
from robloxlx.graphics.vulkan import run_vulkan_smoke

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_BLOCKED = 2


def _state_dir() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return base / "robloxlx" / "logs"


def _print_status(items: dict[str, str]) -> None:
    width = max(map(len, items))
    for key, value in items.items():
        print(f"{key:<{width}} : {value}")


def command_doctor(_: argparse.Namespace) -> int:
    _print_status(collect_diagnostics())
    print("Roblox compatibility : UNKNOWN / NOT TESTED")
    return EXIT_OK


def command_verify(_: argparse.Namespace) -> int:
    client_value = os.environ.get("ROBLOXLX_CLIENT_PATH")
    if not client_value:
        print("Client integrity: UNKNOWN (no client path configured; no client downloaded)")
        print("Only an official source and a verifiable publisher signature can establish provenance.")
        return EXIT_BLOCKED
    path = Path(client_value).expanduser()
    if not path.exists():
        print(f"Client integrity: FAILED (configured path does not exist: {path})")
        return EXIT_ERROR
    candidate = path / "Contents/MacOS/RobloxPlayer" if path.is_dir() and path.suffix == ".app" else path
    if not candidate.is_file():
        print("Client integrity: UNKNOWN (path is not a supported executable file or .app bundle)")
        return EXIT_BLOCKED
    digest = hashlib.sha256()
    try:
        with candidate.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        print(f"Client integrity: FAILED ({exc})")
        return EXIT_ERROR
    print(f"SHA-256 (local measurement only): {digest.hexdigest()}")
    print("Client integrity: UNKNOWN (no trusted Roblox signature/hash baseline configured)")
    return EXIT_BLOCKED


def command_compatibility(_: argparse.Namespace) -> int:
    darling = detect_darling()
    print(f"Darling runtime: {darling.version if darling else 'NOT FOUND'}")
    print("Target: macOS desktop executable through Darling API translation; no guest OS or VM")
    print("Independent Mach-O test: NOT RUN (use `robloxlx darling-test`)")
    print("Roblox compatibility and gameplay: UNKNOWN")
    print("No client patches, injected shims, protocol modifications, or anti-cheat changes are implemented.")
    return EXIT_OK


def command_launch(args: argparse.Namespace) -> int:
    if args.program:
        try:
            executable = resolve_macos_executable(Path(args.program))
        except (FileNotFoundError, ValueError) as exc:
            print(f"Launch error: {exc}")
            return EXIT_ERROR
        darling = detect_darling()
        if not darling:
            if args.dry_run:
                print(f"Program check: valid host-architecture Mach-O executable: {executable}")
            print("Launch blocked: Darling was not found; no process started.")
            return EXIT_BLOCKED
        if args.dry_run:
            try:
                command = build_darling_command(darling, executable, args.program_args)
            except (FileNotFoundError, ValueError) as exc:
                print(f"Launch plan: invalid program: {exc}")
                return EXIT_ERROR
            print(f"Launch plan: {' '.join(command)}")
            print("No process started.")
            return EXIT_OK
        try:
            result = run_darling(
                darling, executable, args.program_args, _state_dir() / "darling-launch.log",
                prefix=Path(args.prefix) if args.prefix else None,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Launch error: {exc}")
            return EXIT_ERROR
        print(f"Darling process exited with status {result}; log: {_state_dir() / 'darling-launch.log'}")
        return result if result >= 0 else EXIT_ERROR
    if args.dry_run:
        details = collect_diagnostics()
        _print_status(details)
        print("Launch plan: BLOCKED (provide --program with a local macOS desktop executable)")
        return EXIT_BLOCKED
    print("Launch blocked: provide --program with an existing macOS executable.")
    return EXIT_BLOCKED


def command_logs(_: argparse.Namespace) -> int:
    directory = _state_dir()
    if not directory.is_dir():
        print(f"No ROBLOX-LX logs found at {directory}")
        return EXIT_OK
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix == ".log")
    if not files:
        print(f"No ROBLOX-LX logs found at {directory}")
        return EXIT_OK
    for path in files:
        print(path)
    return EXIT_OK


def command_graphics_test(args: argparse.Namespace) -> int:
    result = run_vulkan_smoke(args.frames)
    print(f"Vulkan graphics test: {'PASS' if result.passed else 'BLOCKED'}")
    print(f"GPU: {result.device}")
    print(result.detail)
    return EXIT_OK if result.passed else EXIT_BLOCKED


def command_darling_test(_: argparse.Namespace) -> int:
    log = _state_dir() / "darling-test.log"
    result = test_darling_runtime(log)
    print(f"Darling independent Mach-O test: {'PASS' if result.passed else 'BLOCKED'}")
    print(result.detail)
    if log.exists():
        print(f"Log: {log}")
    return EXIT_OK if result.passed else EXIT_BLOCKED


def command_self_test(_: argparse.Namespace) -> int:
    suite = unittest.defaultTestLoader.discover("tests/unit")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return EXIT_OK if result.wasSuccessful() else EXIT_ERROR


def command_metal_test(args: argparse.Namespace) -> int:
    log = _state_dir() / "metal-test.log"
    result = test_metal_runtime(log, driver=Path(args.vulkan_driver) if args.vulkan_driver else None,
                                library=Path(args.metal_library) if args.metal_library else None)
    print(f"Darling Metal buffer test: {'PASS' if result.passed else 'BLOCKED'}")
    print(result.detail)
    if log.exists():
        print(f"Log: {log}")
    print("macOS window presentation and Roblox: UNKNOWN")
    return EXIT_OK if result.passed else EXIT_BLOCKED


def command_network_test(_: argparse.Namespace) -> int:
    log = _state_dir() / "network-test.log"
    result = test_network_runtime(log)
    print(f"Darling DNS/TCP loopback test: {'PASS' if result.passed else 'BLOCKED'}")
    print(result.detail)
    if log.exists():
        print(f"Log: {log}")
    return EXIT_OK if result.passed else EXIT_BLOCKED


def command_cleanup(_: argparse.Namespace) -> int:
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "robloxlx" / "tmp"
    if not cache.exists():
        print("No ROBLOX-LX temporary files to clean.")
        return EXIT_OK
    if cache.is_symlink() or not cache.is_dir():
        print(f"Refusing to clean unexpected path: {cache}")
        return EXIT_ERROR
    shutil.rmtree(cache)
    print(f"Removed ROBLOX-LX temporary data: {cache}")
    return EXIT_OK


def command_window_test(args: argparse.Namespace) -> int:
    log = _state_dir() / "window-test.log"
    result = test_window_runtime(Path(args.executable), log,
                                 driver=Path(args.vulkan_driver) if args.vulkan_driver else None,
                                 wsi=args.wsi)
    print(f"macOS Vulkan WSI test: {'PASS' if result.passed else 'BLOCKED'}")
    print(result.detail)
    print(f"Log: {log}")
    print("AppKit/CAMetalLayer and Roblox: UNKNOWN")
    return EXIT_OK if result.passed else EXIT_BLOCKED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="robloxlx", description="ROBLOX-LX compatibility diagnostics")
    sub = parser.add_subparsers(dest="command", required=True)
    commands = {
        "doctor": (command_doctor, "Inspect the Linux host without changing it."),
        "verify": (command_verify, "Measure a configured client file; cannot establish official provenance."),
        "compatibility": (command_compatibility, "Show current evidence-backed compatibility status."),
        "launch": (command_launch, "Run a local macOS executable through an installed Darling runtime."),
        "logs": (command_logs, "List ROBLOX-LX log files."),
        "graphics-test": (command_graphics_test, "Run a standalone Vulkan-only GPU/window smoke test."),
        "darling-test": (command_darling_test, "Build and run a standalone macOS syscall executable in a temporary Darling prefix."),
        "metal-test": (command_metal_test, "Build and run independent Metal buffer commands through Darling."),
        "window-test": (command_window_test, "Run the independently built macOS Metal/Vulkan window fixture."),
        "network-test": (command_network_test, "Test macOS DNS and TCP loopback through Darling."),
        "self-test": (command_self_test, "Run the local unit test suite."),
        "cleanup": (command_cleanup, "Remove only ROBLOX-LX temporary cache files."),
    }
    for name, (handler, help_text) in commands.items():
        cmd = sub.add_parser(name, help=help_text)
        cmd.set_defaults(handler=handler)
    sub.choices["launch"].add_argument("--dry-run", action="store_true", help="Report readiness without starting a process.")
    sub.choices["launch"].add_argument("--program", help="Existing macOS Mach-O executable or .app bundle on the Linux host.")
    sub.choices["launch"].add_argument("--prefix", help="Use this existing Darling prefix (never created by ROBLOX-LX).")
    sub.choices["launch"].add_argument("program_args", nargs=argparse.REMAINDER, help="Arguments passed after --program PATH.")
    sub.choices["graphics-test"].add_argument("--frames", type=int, default=3, help="Frames to present (1-1000).")
    sub.choices["metal-test"].add_argument("--vulkan-driver", help="Use this ICD manifest for the independent Metal test; default selects physical hardware.")
    sub.choices["metal-test"].add_argument("--metal-library", help="Link the independent fixture against this source-built Metal implementation.")
    sub.choices["window-test"].add_argument("--executable", required=True, help="Source-built independent window-probe Mach-O.")
    sub.choices["window-test"].add_argument("--vulkan-driver", help="Physical Vulkan ICD manifest.")
    sub.choices["window-test"].add_argument("--wsi", choices=("wayland", "x11"), default="wayland")
    version = sub.add_parser("version", help="Show version.")
    version.set_defaults(handler=lambda _: print(f"ROBLOX-LX {__version__}") or EXIT_OK)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.handler(args))
    except (OSError, ValueError) as exc:
        print(f"robloxlx: error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
