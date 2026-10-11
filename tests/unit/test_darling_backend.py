import shutil
import subprocess
import tempfile
import unittest
import plistlib
import struct
from pathlib import Path
import platform
from unittest.mock import patch

from robloxlx.compatibility.darling import (
    DarlingRuntime, build_darling_command, detect_darling, host_path_to_darling,
    resolve_macos_executable, run_darling, test_darling_runtime as darling_runtime_smoke,
)


def _make_macho(path: Path, *, architecture: str | None = None) -> None:
    if architecture is None:
        architecture = "arm64" if platform.machine().lower() in ("aarch64", "arm64") else "x86_64"
    cpu = 0x0100000C if architecture == "arm64" else 0x01000007
    header = bytearray(32)
    header[:4] = bytes.fromhex("cffaedfe")
    struct.pack_into("<I", header, 4, cpu)
    struct.pack_into("<I", header, 12, 2)  # MH_EXECUTE
    path.write_bytes(header)
    path.chmod(0o755)


class DarlingBackendTests(unittest.TestCase):
    @patch("robloxlx.compatibility.darling.shutil.which", return_value=None)
    def test_missing_darling_is_reported(self, _which):
        self.assertIsNone(detect_darling())

    @patch("robloxlx.compatibility.darling.Path.is_file", return_value=False)
    @patch("robloxlx.compatibility.darling.shutil.which", return_value="/usr/bin/darling")
    @patch("robloxlx.compatibility.darling.subprocess.run", side_effect=AssertionError("must not execute Darling"))
    def test_discovery_reports_missing_server_without_starting_runtime(self, _run, _which, _is_file):
        found = detect_darling()
        self.assertEqual(found.executable, Path("/usr/bin/darling"))
        self.assertIn("darlingserver NOT FOUND", found.version)

    def test_builds_shell_free_command_and_maps_host_path(self):
        with tempfile.TemporaryDirectory() as folder:
            program = Path(folder) / "hello app"
            _make_macho(program)
            runtime = DarlingRuntime(Path("/usr/bin/darling"), "Darling test")
            command = build_darling_command(runtime, program, ["arg with spaces", "$(literal)"])
            self.assertEqual(command[:3], ["/usr/bin/darling", "shell", f"/Volumes/SystemRoot{program}"])
            self.assertEqual(command[3:], ["arg with spaces", "$(literal)"])
            self.assertEqual(host_path_to_darling(program), f"/Volumes/SystemRoot{program}")

    def test_rejects_missing_program(self):
        runtime = DarlingRuntime(Path("/usr/bin/darling"), "Darling test")
        with self.assertRaises(FileNotFoundError):
            build_darling_command(runtime, Path("/does/not/exist/program"))

    def test_rejects_elf_and_wrong_architecture(self):
        with tempfile.TemporaryDirectory() as folder:
            program = Path(folder) / "not-macos"
            program.write_bytes(b"\x7fELF" + bytes(60))
            program.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "not a 64-bit Mach-O"):
                resolve_macos_executable(program)
            other_arch = "x86_64" if platform.machine().lower() in ("aarch64", "arm64") else "arm64"
            _make_macho(program, architecture=other_arch)
            with self.assertRaisesRegex(ValueError, "architecture mismatch"):
                resolve_macos_executable(program)

    def test_resolves_app_bundle_executable_from_plist(self):
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder) / "Test.app"
            contents = bundle / "Contents"
            executable = contents / "MacOS" / "TestPlayer"
            executable.parent.mkdir(parents=True)
            _make_macho(executable)
            with (contents / "Info.plist").open("wb") as output:
                plistlib.dump({"CFBundleExecutable": "TestPlayer"}, output)
            self.assertEqual(resolve_macos_executable(bundle), executable.resolve())

    def test_rejects_app_bundle_executable_outside_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bundle = root / "Test.app"
            contents = bundle / "Contents"
            (contents / "MacOS").mkdir(parents=True)
            outside = root / "outside"
            _make_macho(outside)
            with (contents / "Info.plist").open("wb") as output:
                plistlib.dump({"CFBundleExecutable": "../../outside"}, output)
            with self.assertRaisesRegex(ValueError, "safe CFBundleExecutable"):
                resolve_macos_executable(bundle)

    def test_process_capture_and_private_log(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            executable = root / "fake-darling"
            executable.write_text("#!/bin/sh\nprintf 'FAKE_DARLING_OK:%s\\n' \"$2\"\n", encoding="utf-8")
            executable.chmod(0o755)
            program = root / "independent-macos-app"
            _make_macho(program)
            log = root / "logs" / "darling.log"
            status = run_darling(DarlingRuntime(executable, "fake"), program, [], log)
            self.assertEqual(status, 0)
            self.assertIn("FAKE_DARLING_OK:/Volumes/SystemRoot", log.read_text())
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)

    @patch("robloxlx.compatibility.darling.detect_darling", return_value=None)
    def test_runtime_smoke_blocks_without_darling(self, _detect):
        result = darling_runtime_smoke()
        self.assertFalse(result.passed)
        self.assertIn("Darling NOT FOUND", result.detail)

    def test_process_timeout_terminates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runtime_bin = root / "fake-darling"
            runtime_bin.write_text("#!/bin/sh\nsleep 10\n", encoding="utf-8")
            runtime_bin.chmod(0o755)
            program = root / "slow"
            _make_macho(program)
            result = run_darling(DarlingRuntime(runtime_bin, "fake"), program, [], root / "run.log", timeout=0.05)
            self.assertEqual(result, 124)
            self.assertIn("timed out", (root / "run.log").read_text())


class DarlingIndependentExecutableTests(unittest.TestCase):
    """Build a real Mach-O fixture, then run it only if Darling is installed."""

    def _build_fixture(self, root: Path) -> Path:
        clang = shutil.which("clang")
        linker = shutil.which("ld64.lld")
        if not clang or not linker:
            self.skipTest("local Clang and ld64.lld Mach-O build tools are required")
        # The fixture uses only Darwin's write/exit syscalls; no SDK or third-
        # party source is linked into the independent compatibility probe.
        fixture = Path(__file__).parents[2] / "src/robloxlx/compatibility/fixtures/macho_hello.s"
        obj, executable = root / "hello.o", root / "hello"
        subprocess_result = subprocess.run(
            [clang, "-target", "x86_64-apple-macos10.15", "-c", str(fixture), "-o", str(obj)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(subprocess_result.returncode, 0, subprocess_result.stderr)
        subprocess_result = subprocess.run(
            [linker, "-arch", "x86_64", "-platform_version", "macos", "10.15", "10.15",
             "-e", "_start", "-o", str(executable), str(obj)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(subprocess_result.returncode, 0, subprocess_result.stderr)
        self.assertEqual(executable.read_bytes()[:4], bytes.fromhex("cffaedfe"))
        return executable

    def test_macho_hello_fixture_compiles_and_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = self._build_fixture(Path(folder))
            self.assertEqual(resolve_macos_executable(executable), executable.resolve())

    def test_macho_hello_executes_under_darling(self):
        darling = shutil.which("darling")
        if not darling:
            self.skipTest("Darling runtime is not installed")
        if not Path(darling).with_name("darlingserver").is_file():
            self.skipTest("Darling launcher is installed without its darlingserver helper")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            executable = self._build_fixture(root)
            prefix = root / "dprefix"
            prefix.mkdir(mode=0o700)
            from robloxlx.compatibility.darling import run_darling
            status = run_darling(
                DarlingRuntime(Path(darling).resolve(), "detected"), executable, [], root / "run.log",
                prefix=prefix, timeout=30,
            )
            self.assertEqual(status, 0)
            self.assertIn("ROBLOXLX_MACHO_OK", (root / "run.log").read_text())


if __name__ == "__main__":
    unittest.main()
