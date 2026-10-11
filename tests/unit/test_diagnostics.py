import unittest
from unittest.mock import patch

from robloxlx.diagnostics import collect_diagnostics


class DiagnosticsTests(unittest.TestCase):
    @patch("robloxlx.diagnostics.shutil.which", return_value=None)
    @patch("robloxlx.diagnostics.platform.release", return_value="test-kernel")
    @patch("robloxlx.diagnostics.platform.machine", return_value="x86_64")
    def test_missing_optional_probes_are_unknown(self, _machine, _release, _which):
        result = collect_diagnostics()
        self.assertEqual(result["kernel"], "test-kernel")
        self.assertEqual(result["architecture"], "x86_64")
        self.assertEqual(result["gpu"], "UNKNOWN")
        self.assertNotIn("darling", result)


if __name__ == "__main__":
    unittest.main()
