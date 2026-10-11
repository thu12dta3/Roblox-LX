import unittest
from unittest.mock import patch, Mock

from robloxlx.graphics.vulkan import run_vulkan_smoke


class VulkanGraphicsSmokeTests(unittest.TestCase):
    @patch("robloxlx.graphics.vulkan.shutil.which", return_value=None)
    def test_missing_vkcube_is_blocked(self, _which):
        result = run_vulkan_smoke()
        self.assertFalse(result.passed)
        self.assertEqual(result.detail, "vkcube NOT FOUND")

    def test_rejects_invalid_frame_count(self):
        with self.assertRaises(ValueError):
            run_vulkan_smoke(0)

    @patch.dict("os.environ", {"WAYLAND_DISPLAY": "wayland-test"}, clear=True)
    @patch("robloxlx.graphics.vulkan.subprocess.run")
    @patch("robloxlx.graphics.vulkan.shutil.which", return_value="/usr/bin/vkcube")
    def test_runs_vulkan_wsi_without_graphics_fallback(self, _which, run):
        run.return_value = Mock(returncode=0, stdout="", stderr=(
            "Selected GPU 0: Test Hardware, type: DiscreteGpu, apiVersion: 1.4"
        ))
        result = run_vulkan_smoke(2)
        self.assertTrue(result.passed)
        self.assertEqual(run.call_args.args[0], ["/usr/bin/vkcube", "--wsi", "wayland", "--c", "2"])
        self.assertIn("OpenGL was not used", result.detail)

    @patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True)
    @patch("robloxlx.graphics.vulkan.subprocess.run")
    @patch("robloxlx.graphics.vulkan.shutil.which", return_value="/usr/bin/vkcube")
    def test_rejects_software_vulkan_device(self, _which, run):
        run.return_value = Mock(returncode=0, stdout="", stderr=(
            "Selected GPU 0: llvmpipe, type: Cpu, apiVersion: 1.4"
        ))
        result = run_vulkan_smoke(2)
        self.assertFalse(result.passed)
        self.assertIn("non-hardware GPU", result.detail)


if __name__ == "__main__":
    unittest.main()
