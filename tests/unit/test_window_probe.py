"""Process orchestration checks; mocked results are not GPU compatibility evidence."""
import os
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

from robloxlx.compatibility.darling import (
    DarlingRuntime, DarlingSmokeResult, test_window_runtime as window_probe,
)
from robloxlx.cli import build_parser


class WindowProbeTests(unittest.TestCase):
    def test_invalid_wsi_does_not_start_runtime(self):
        with patch('robloxlx.compatibility.darling.detect_darling') as discover:
            result = window_probe(Path('/probe'), Path('/log'), wsi='opengl')
        self.assertFalse(result.passed)
        discover.assert_not_called()

    def test_missing_runtime_is_reported(self):
        with patch('robloxlx.compatibility.darling.detect_darling', return_value=None):
            result = window_probe(Path('/probe'), Path('/log'))
        self.assertFalse(result.passed)
        self.assertIn('NOT FOUND', result.detail)

    @patch.dict(os.environ, {}, clear=True)
    def test_wsi_environment_is_scoped_to_probe(self):
        runtime = DarlingRuntime(Path('/darling'), 'test')
        with patch('robloxlx.compatibility.darling.detect_darling', return_value=runtime), \
             patch('robloxlx.compatibility.darling.resolve_macos_executable', return_value=Path('/probe')), \
             patch('robloxlx.compatibility.darling.select_hardware_vulkan_environment', return_value={'VK_DRIVER_FILES': '/icd.json'}), \
             patch('robloxlx.compatibility.darling._run_independent_probe', return_value=DarlingSmokeResult(True, 'orchestration only')) as run:
            result = window_probe(Path('/probe'), Path('/log'), wsi='x11')
        self.assertTrue(result.passed)
        self.assertEqual(run.call_args.args[-1], {
            'VK_DRIVER_FILES': '/icd.json', 'ROBLOXLX_METAL_WSI': 'x11', 'SDL_VIDEODRIVER': 'x11',
        })
        self.assertNotIn('SDL_VIDEODRIVER', os.environ)

    def test_cli_requires_explicit_independent_executable(self):
        args = build_parser().parse_args(['window-test', '--executable', '/probe', '--wsi', 'x11'])
        self.assertEqual(args.executable, '/probe')
        self.assertEqual(args.wsi, 'x11')

    def test_elf_is_rejected_before_process_execution(self):
        runtime = DarlingRuntime(Path('/darling'), 'test')
        with patch('robloxlx.compatibility.darling.detect_darling', return_value=runtime), \
             patch('robloxlx.compatibility.darling._run_independent_probe') as run:
            result = window_probe(Path('/bin/true'), Path('/log'))
        self.assertFalse(result.passed)
        run.assert_not_called()


@unittest.skipUnless(os.environ.get("ROBLOXLX_WINDOW_PROBE"), "source-built WSI fixture not configured")
class WindowRuntimeIntegrationTests(unittest.TestCase):
    def _run_wsi(self, wsi):
        executable = Path(os.environ["ROBLOXLX_WINDOW_PROBE"])
        with tempfile.TemporaryDirectory(prefix="robloxlx-window-test-log-") as directory:
            log = Path(directory) / "window.log"
            result = window_probe(executable, log, wsi=wsi)
            self.assertTrue(result.passed, result.detail)
            output = log.read_text()
            self.assertIn("WSI_PRESENTED:30 frames", output)
            self.assertIn("WSI_METAL_PIXELS_VERIFIED", output)
            self.assertIn("METAL_RUNTIME_TEARDOWN_COMPLETE", output)
            self.assertIn("Probe shutdown exit 0", output)
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)

    def test_real_macos_wayland_presentation(self):
        if not os.environ.get("WAYLAND_DISPLAY"):
            self.skipTest("Wayland display is absent")
        self._run_wsi("wayland")

    def test_real_macos_x11_presentation(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("X11/XWayland display is absent")
        self._run_wsi("x11")


if __name__ == '__main__':
    unittest.main()
