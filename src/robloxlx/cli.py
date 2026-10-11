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
from robloxlx.diagnostics import collect_diagnostics

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
    print("Roblox compatibility : BLOCKED / NOT VALIDATED")
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
    print("Darling backend: PARTIAL (detection only; no isolated runtime manager implemented)")
    print("Roblox desktop on Linux: BLOCKED by official platform support status; no launch path validated")
    print("MacOBlox: UNKNOWN for ROBLOX-LX policy; published implementation reports injected compatibility shims")
    print("No anti-cheat bypass, client patching, memory modification, or protocol spoofing is implemented.")
    return EXIT_OK


def command_launch(args: argparse.Namespace) -> int:
    if args.dry_run:
        details = collect_diagnostics()
        _print_status(details)
        print("Launch plan: BLOCKED (Darling + official-client workflow is not validated; no process started)")
        return EXIT_BLOCKED
    print("Launch blocked: Roblox-LX has no validated, policy-compliant Roblox launch backend.")
    print("No client was started and no account credentials were accessed.")
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
    parser = argparse.ArgumentParser(prog="robloxlx", description="ROBLOX-LX compatibility diagnostics")
    sub = parser.add_subparsers(dest="command", required=True)
    commands = {
        "doctor": (command_doctor, "Inspect the Linux host without changing it."),
        "verify": (command_verify, "Measure a configured client file; cannot establish official provenance."),
        "compatibility": (command_compatibility, "Show current evidence-backed compatibility status."),
        "launch": (command_launch, "Launch only when a validated backend is available."),
        "logs": (command_logs, "List ROBLOX-LX log files."),
        "self-test": (command_self_test, "Run the local unit test suite."),
        "cleanup": (command_cleanup, "Remove only ROBLOX-LX temporary cache files."),
    }
    for name, (handler, help_text) in commands.items():
        cmd = sub.add_parser(name, help=help_text)
        cmd.set_defaults(handler=handler)
    sub.choices["launch"].add_argument("--dry-run", action="store_true", help="Report readiness without starting a process.")
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
