"""Command-line interface for Linux-native ROBLOX-LX diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import unittest
from pathlib import Path

from robloxlx import __version__
from robloxlx.diagnostics import collect_diagnostics
from robloxlx.graphics.vulkan import run_vulkan_smoke

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_BLOCKED = 2


def _state_dir() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return base / "robloxlx" / "logs"


def _print_status(items: dict[str, str]) -> None:
    width = max((len(key) for key in items), default=0)
    for key, value in items.items():
        print(f"{key:<{width}} : {value}")


def command_doctor(_: argparse.Namespace) -> int:
    _print_status(collect_diagnostics())
    return EXIT_OK


def command_compatibility(_: argparse.Namespace) -> int:
    print("Target: traditional Linux desktop")
    print("Native Roblox client: NOT IMPLEMENTED / NOT VERIFIED")
    print("Host Vulkan smoke test: available via `robloxlx graphics-test`")
    print("Host graphics support does not establish Roblox compatibility.")
    print("No macOS runtime, client patching, code injection, or anti-cheat bypass is included.")
    return EXIT_OK


def command_verify(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser()
    if not path.is_file():
        print(f"Verification failed: not a regular file: {path}")
        return EXIT_ERROR
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        print(f"Verification failed: {exc}")
        return EXIT_ERROR
    print(f"File: {path}")
    print(f"SHA-256: {digest.hexdigest()}")
    print("Authenticity: UNKNOWN (no trusted publisher signature or digest baseline configured)")
    return EXIT_OK


def command_logs(_: argparse.Namespace) -> int:
    directory = _state_dir()
    if not directory.is_dir():
        print(f"No ROBLOX-LX logs found at {directory}")
        return EXIT_OK
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix == ".log")
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


def command_self_test(_: argparse.Namespace) -> int:
    suite = unittest.defaultTestLoader.discover("tests/unit")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return EXIT_OK if result.wasSuccessful() else EXIT_ERROR


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="robloxlx", description="Linux-native diagnostics (not a Roblox client)")
    sub = parser.add_subparsers(dest="command", required=True)
    commands = {
        "doctor": (command_doctor, "Inspect Linux host capabilities without changing the system."),
        "compatibility": (command_compatibility, "Show the current evidence-backed compatibility status."),
        "verify": (command_verify, "Calculate a file SHA-256; this does not prove authenticity."),
        "logs": (command_logs, "List ROBLOX-LX log files."),
        "graphics-test": (command_graphics_test, "Run a standalone hardware Vulkan presentation smoke test."),
        "self-test": (command_self_test, "Run the local unit test suite from a source checkout."),
        "cleanup": (command_cleanup, "Remove only ROBLOX-LX temporary cache files."),
        "version": (lambda _: print(f"ROBLOX-LX {__version__}") or EXIT_OK, "Show version."),
    }
    for name, (handler, help_text) in commands.items():
        command = sub.add_parser(name, help=help_text)
        command.set_defaults(handler=handler)
    sub.choices["verify"].add_argument("path", help="Path to a local regular file.")
    sub.choices["graphics-test"].add_argument("--frames", type=int, default=3, help="Frames to present (1-1000).")
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
