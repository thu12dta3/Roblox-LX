"""Safe discovery and command construction for a user-installed Wine runtime.

This module does not install Wine, modify Windows executables, or work around
application security controls. Roblox launch is intentionally not exposed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess  # nosec B404 -- invoked only for a fixed --version probe


@dataclass(frozen=True)
class WineRuntime:
    executable: Path
    version: str


def detect_wine(timeout: float = 3.0) -> WineRuntime | None:
    """Return an installed Wine binary and its reported version, if available."""
    resolved = shutil.which("wine")
    if not resolved:
        return None
    executable = Path(resolved).resolve()
    try:
        result = subprocess.run(  # nosec B603 -- fixed version probe; no shell or user arguments
            [str(executable), "--version"], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return WineRuntime(executable, "VERSION UNKNOWN")
    lines = (result.stdout or result.stderr).strip().splitlines()
    return WineRuntime(executable, lines[0][:160] if lines else "VERSION UNKNOWN")


def build_wine_command(
    runtime: WineRuntime, windows_program: Path, arguments: list[str] | None = None
) -> list[str]:
    """Build an argv vector for an existing local program; never invoke a shell."""
    program = windows_program.expanduser().resolve(strict=True)
    if not program.is_file():
        raise ValueError(f"Windows program is not a regular file: {program}")
    return [str(runtime.executable), str(program), *(arguments or [])]
