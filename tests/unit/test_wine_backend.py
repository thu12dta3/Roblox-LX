import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from robloxlx.compatibility.wine import WineRuntime, build_wine_command, detect_wine


class WineBackendTests(unittest.TestCase):
    @patch("robloxlx.compatibility.wine.shutil.which", return_value=None)
    def test_missing_wine_is_reported(self, _which):
        self.assertIsNone(detect_wine())

    def test_builds_argv_without_shell_interpretation(self):
        with tempfile.TemporaryDirectory() as folder:
            program = Path(folder) / "desktop test.exe"
            program.touch()
            runtime = WineRuntime(Path("/usr/bin/wine"), "wine-test")
            argv = build_wine_command(runtime, program, ["argument with spaces", "$(literal)"])
        self.assertEqual(argv[0], "/usr/bin/wine")
        self.assertTrue(argv[1].endswith("desktop test.exe"))
        self.assertEqual(argv[2:], ["argument with spaces", "$(literal)"])

    def test_rejects_missing_program(self):
        runtime = WineRuntime(Path("/usr/bin/wine"), "wine-test")
        with self.assertRaises(FileNotFoundError):
            build_wine_command(runtime, Path("/does/not/exist/program.exe"))


if __name__ == "__main__":
    unittest.main()
