"""Read-only, best-effort diagnostics for a traditional Linux desktop."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess  # nosec B404 -- fixed, read-only probe arguments
from ctypes.util import find_library
from pathlib import Path


def _run(args: list[str], timeout: float = 3.0) -> str | None:
    executable = shutil.which(args[0])
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, *args[1:]], capture_output=True, text=True,
            timeout=timeout, check=False,
        )  # nosec B603 -- fixed read-only probe, no shell or user arguments
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0][:240] if output else None


def _run_matching(args: list[str], markers: tuple[str, ...]) -> str | None:
    executable = shutil.which(args[0])
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, *args[1:]], capture_output=True, text=True,
            timeout=5.0, check=False,
        )  # nosec B603 -- fixed read-only probe, no shell or user arguments
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = (result.stdout + "\n" + result.stderr).splitlines()
    normalized = tuple(marker.lower().replace(" ", "") for marker in markers)
    selected = [
        line.strip() for line in lines
        if any(marker in line.lower().replace(" ", "") for marker in normalized)
    ]
    return "; ".join(selected[:4])[:500] if selected else None


def _probe_vulkan_wsi(session: str) -> str:
    """Report Vulkan instance surface extensions when vulkaninfo exposes them."""
    executable = shutil.which("vulkaninfo")
    if not executable:
        return "UNKNOWN (vulkaninfo NOT FOUND)"
    try:
        result = subprocess.run(
            [executable, "--summary"], capture_output=True, text=True,
            timeout=5.0, check=False,
        )  # nosec B603 -- fixed read-only Vulkan capability probe
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN (vulkaninfo probe failed)"
    if result.returncode:
        return f"UNKNOWN (vulkaninfo exit {result.returncode})"
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    available = {
        line.split(":", 1)[0].strip()
        for line in output.splitlines()
        if line.strip().startswith("VK_") and ": extension revision" in line
    }
    expected = {
        "Wayland": "VK_KHR_wayland_surface",
        "X11": "VK_KHR_xcb_surface",
    }.get(session)
    names = ["VK_KHR_surface"]
    if expected:
        names.append(expected)
    if not available:
        return "UNKNOWN (instance extension list absent from vulkaninfo summary)"
    return "; ".join(
        f"{name}={'FOUND' if name in available else 'NOT FOUND'}" for name in names
    )


def _os_name() -> str:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.partition("=")[2].strip('"')
    except OSError:
        pass
    return platform.system() or "UNKNOWN"


def collect_diagnostics() -> dict[str, str]:
    """Collect host metadata and command/library availability without changing the system."""
    session = "Wayland" if os.environ.get("WAYLAND_DISPLAY") else (
        "X11" if os.environ.get("DISPLAY") else "UNKNOWN"
    )
    gpu = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if not gpu:
        gpu = _run(["lspci", "-nn", "-d", "::0300"])
    vulkan = _run_matching(
        ["vulkaninfo", "--summary"], ("apiversion", "devicename", "drivername")
    )
    libraries = {
        "Vulkan loader": "vulkan",
        "PulseAudio": "pulse",
        "PipeWire": "pipewire-0.3",
        "X11": "X11",
        "XInput2": "Xi",
        "Wayland client": "wayland-client",
    }
    library_status = [
        f"{label}={'FOUND' if find_library(name) else 'NOT FOUND'}"
        for label, name in libraries.items()
    ]
    return {
        "distribution": _os_name(),
        "kernel": platform.release() or "UNKNOWN",
        "architecture": platform.machine() or "UNKNOWN",
        "graphical_session": session,
        "gpu": gpu or "UNKNOWN",
        "nvidia_driver": _run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"]
        ) or "UNKNOWN",
        "vulkan": vulkan or (
            "UNKNOWN (vulkaninfo present; no summary fields returned)"
            if shutil.which("vulkaninfo") else "UNKNOWN"
        ),
        "host_vulkan_wsi_extensions": _probe_vulkan_wsi(session),
        "vulkan_graphics_tools": ", ".join(
            name for name in ("vulkaninfo", "vkcube") if shutil.which(name)
        ) or "UNKNOWN",
        "audio_tools": ", ".join(
            name for name in ("pw-cat", "pacat", "pactl") if shutil.which(name)
        ) or "UNKNOWN",
        "input_tools": ", ".join(
            name for name in ("xinput", "libinput") if shutil.which(name)
        ) or "UNKNOWN",
        "network_tools": ", ".join(
            name for name in ("getent", "resolvectl") if shutil.which(name)
        ) or "UNKNOWN",
        "host_libraries": ", ".join(library_status),
        "optional_probe_tools": ", ".join(
            name for name in ("vulkaninfo", "vkcube", "nvidia-smi", "lspci")
            if shutil.which(name)
        ) or "NONE FOUND",
    }
