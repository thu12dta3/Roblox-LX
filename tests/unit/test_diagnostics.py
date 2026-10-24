import unittest
from unittest.mock import Mock, patch

from robloxlx.diagnostics import _probe_vulkan_wsi, collect_diagnostics


class DiagnosticsTests(unittest.TestCase):
    @patch("robloxlx.diagnostics.shutil.which", return_value=None)
    @patch("robloxlx.diagnostics.platform.release", return_value="test-kernel")
    @patch("robloxlx.diagnostics.platform.machine", return_value="x86_64")
    def test_missing_optional_probes_are_unknown(self, _machine, _release, _which):
        result = collect_diagnostics()
        self.assertEqual(result["kernel"], "test-kernel")
        self.assertEqual(result["architecture"], "x86_64")
        self.assertEqual(result["gpu"], "UNKNOWN")
        self.assertIn("vulkan_graphics_tools", result)
        self.assertIn("audio_tools", result)
        self.assertNotIn("darling_macos_runtime", result)
        self.assertNotIn("opengl", result)

    def test_vulkan_wsi_parser_checks_active_session_extension(self):
        summary = """Instance Extensions: count = 2
VK_KHR_surface : extension revision 25
VK_KHR_wayland_surface : extension revision 6
Devices:
GPU0:
"""
        with patch("robloxlx.diagnostics.shutil.which", return_value="/usr/bin/vulkaninfo") as _which:
            with patch("robloxlx.diagnostics.subprocess.run") as run:
                run.return_value = Mock(returncode=0, stdout=summary, stderr="")
                self.assertEqual(
                    _probe_vulkan_wsi("Wayland"),
                    "VK_KHR_surface=FOUND; VK_KHR_wayland_surface=FOUND",
                )
                self.assertIn("VK_KHR_xcb_surface=NOT FOUND", _probe_vulkan_wsi("X11"))

    @patch("robloxlx.diagnostics.shutil.which", return_value=None)
    def test_vulkan_wsi_is_unknown_without_vulkaninfo(self, _which):
        self.assertEqual(_probe_vulkan_wsi("Wayland"), "UNKNOWN (vulkaninfo NOT FOUND)")


if __name__ == "__main__":
    unittest.main()
