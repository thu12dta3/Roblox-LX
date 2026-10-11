"""Read-only, best-effort host diagnostics."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess  # nosec B404 -- used only with fixed, read-only probe arguments
from pathlib import Path


def _run(args: list[str], timeout: float = 3.0) -> str | None:
    executable = shutil.which(args[0])
    if not executable:
        return None
    try:
        result = subprocess.run(  # nosec B603 -- fixed read-only probe, no shell or user arguments
            [executable, *args[1:]], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0][:240] if output else None


def _run_matching(args: list[str], markers: tuple[str, ...]) -> str | None:
    executable = shutil.which(args[0])
    if not executable:
        return None
    try:
        result = subprocess.run(  # nosec B603 -- fixed read-only probe, no shell or user arguments
            [executable, *args[1:]], capture_output=True, text=True,
            timeout=5.0, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = (result.stdout + "\n" + result.stderr).splitlines()
    normalized_markers = tuple(marker.lower().replace(" ", "") for marker in markers)
    selected = [
        line.strip() for line in lines
        if any(marker in line.lower().replace(" ", "") for marker in normalized_markers)
    ]
    return "; ".join(selected[:4])[:500] if selected else None


def _os_name() -> str:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.partition("=")[2].strip('"')
    except OSError:
        pass
    return platform.system() or "UNKNOWN"


def collect_diagnostics() -> dict[str, str]:
    """Collect only host metadata and command availability; never change the system."""
    session = "Wayland" if os.environ.get("WAYLAND_DISPLAY") else (
        "X11" if os.environ.get("DISPLAY") else "UNKNOWN"
    )
    gpu = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if not gpu:
        gpu = _run(["lspci", "-nn", "-d", "::0300"])
    gl = _run_matching(["glxinfo", "-B"], ("opengl vendor", "opengl renderer", "opengl version"))
    vk = _run_matching(["vulkaninfo", "--summary"], ("apiversion", "devicename", "drivername"))
    return {
        "distribution": _os_name(),
        "kernel": platform.release() or "UNKNOWN",
        "architecture": platform.machine() or "UNKNOWN",
        "graphical_session": session,
        "gpu": gpu or "UNKNOWN",
        "nvidia_driver": _run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"]) or "UNKNOWN",
        "opengl": gl or ("UNKNOWN (glxinfo present; no summary fields returned)" if shutil.which("glxinfo") else "UNKNOWN"),
        "vulkan": vk or ("UNKNOWN (vulkaninfo present; no summary fields returned)" if shutil.which("vulkaninfo") else "UNKNOWN"),
        "dependencies": ", ".join(name for name in ("glxinfo", "vulkaninfo", "nvidia-smi", "lspci") if shutil.which(name)) or "NONE OF OPTIONAL PROBES FOUND",
    }
