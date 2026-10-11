import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from robloxlx.compatibility.darling import (
    DarlingRuntime, build_darling_command, detect_darling, host_path_to_darling,
)


class DarlingBackendTests(unittest.TestCase):
    @patch("robloxlx.compatibility.darling.shutil.which", return_value=None)
    def test_missing_darling_is_reported(self, _which):
        self.assertIsNone(detect_darling())

    def test_builds_shell_free_command_and_maps_host_path(self):
        with tempfile.TemporaryDirectory() as folder:
            program = Path(folder) / "hello app"
            program.touch()
            runtime = DarlingRuntime(Path("/usr/bin/darling"), "Darling test")
            command = build_darling_command(runtime, program, ["arg with spaces", "$(literal)"])
            self.assertEqual(command[:3], ["/usr/bin/darling", "shell", f"/Volumes/SystemRoot{program}"])
            self.assertEqual(command[3:], ["arg with spaces", "$(literal)"])
            self.assertEqual(host_path_to_darling(program), f"/Volumes/SystemRoot{program}")

    def test_rejects_missing_program(self):
        runtime = DarlingRuntime(Path("/usr/bin/darling"), "Darling test")
        with self.assertRaises(FileNotFoundError):
            build_darling_command(runtime, Path("/does/not/exist/program"))

    def test_process_capture_and_private_log(self):
        from robloxlx.compatibility.darling import run_darling
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            executable = root / "fake-darling"
            executable.write_text("#!/bin/sh\nprintf 'FAKE_DARLING_OK:%s\\n' \"$2\"\n", encoding="utf-8")
            executable.chmod(0o755)
            program = root / "independent-macos-app"
            program.touch()
            log = root / "logs" / "darling.log"
            status = run_darling(DarlingRuntime(executable, "fake"), program, [], log)
            self.assertEqual(status, 0)
            self.assertIn("FAKE_DARLING_OK:/Volumes/SystemRoot", log.read_text())
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)


class DarlingIndependentExecutableTests(unittest.TestCase):
    """Actual Mach-O run; skipped unless the external runtime exists."""

    def test_macho_hello_executable(self):
        darling = shutil.which("darling")
        clang = shutil.which("clang")
        linker = shutil.which("ld64.lld")
        if not darling or not clang or not linker:
            self.skipTest("Darling and the local Mach-O build tools are required")
        # The fixture uses only Darwin's write/exit syscalls; no SDK or third-
        # party source is linked into the independent compatibility probe.
        fixture = Path(__file__).parent / "fixtures" / "macho_hello.s"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
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
            from robloxlx.compatibility.darling import run_darling
            status = run_darling(
                DarlingRuntime(Path(darling).resolve(), "detected"), executable, [], root / "run.log",
                prefix=root / "dprefix",
            )
            self.assertEqual(status, 0)
            self.assertIn("ROBLOXLX_MACHO_OK", (root / "run.log").read_text())


if __name__ == "__main__":
    unittest.main()
