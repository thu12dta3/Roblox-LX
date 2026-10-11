"""Vulkan-only host graphics probe. It never falls back to OpenGL/Zink."""

from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess  # nosec B404 -- fixed native Vulkan smoke executable


@dataclass(frozen=True)
class VulkanSmokeResult:
    passed: bool
    device: str
    detail: str


def run_vulkan_smoke(frames: int = 3, timeout: float = 30.0) -> VulkanSmokeResult:
    """Run the system vkcube Vulkan renderer for a bounded number of frames."""
    if not 1 <= frames <= 1000:
        raise ValueError("frames must be between 1 and 1000")
    executable = shutil.which("vkcube")
    if not executable:
        return VulkanSmokeResult(False, "UNKNOWN", "vkcube NOT FOUND")
    if os.environ.get("WAYLAND_DISPLAY"):
        wsi = "wayland"
    elif os.environ.get("DISPLAY"):
        wsi = "xcb"
    else:
        return VulkanSmokeResult(False, "UNKNOWN", "no Wayland or X11 display is available")
    try:
        result = subprocess.run(  # nosec B603 -- fixed trusted vkcube argv, no shell
            [executable, "--wsi", wsi, "--c", str(frames)],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return VulkanSmokeResult(False, "UNKNOWN", f"vkcube timed out after {timeout:g}s")
    except OSError as exc:
        return VulkanSmokeResult(False, "UNKNOWN", f"vkcube failed to start: {exc}")
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    device = next((line.strip()[:240] for line in output.splitlines()
                   if "Selected GPU" in line and "type:" in line), "UNKNOWN")
    if result.returncode:
        detail = next((line.strip() for line in reversed(output.splitlines()) if line.strip()), "no diagnostic output")
        return VulkanSmokeResult(False, device, f"vkcube exit {result.returncode}: {detail[:240]}")
    if device == "UNKNOWN":
        return VulkanSmokeResult(False, device, "vkcube exited successfully without reporting a selected GPU")
    device_type = device.lower().partition("type:")[2]
    if "discretegpu" not in device_type and "integratedgpu" not in device_type:
        return VulkanSmokeResult(False, device, "Vulkan smoke used a non-hardware GPU; select a discrete/integrated Vulkan device")
    return VulkanSmokeResult(True, device, f"Vulkan swapchain presented {frames} frame(s) using {wsi}; OpenGL was not used")
