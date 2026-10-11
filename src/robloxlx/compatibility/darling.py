"""Discovery and process management for a user-installed Darling runtime.

The launcher never initializes or edits a DPREFIX. The caller must choose an
existing prefix; Darling may initialize its default prefix when first started.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import signal
import subprocess  # nosec B404 -- fixed probes and explicit, shell-free argv


@dataclass(frozen=True)
class DarlingRuntime:
    executable: Path
    version: str


def detect_darling(timeout: float = 3.0) -> DarlingRuntime | None:
    """Find Darling and read its version, returning UNKNOWN if its probe fails."""
    resolved = shutil.which("darling")
    if not resolved:
        return None
    executable = Path(resolved).resolve()
    try:
        result = subprocess.run(  # nosec B603 -- fixed version probe, no shell
            [str(executable), "--version"], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return DarlingRuntime(executable, "VERSION UNKNOWN")
    lines = (result.stdout or result.stderr).strip().splitlines()
    # Some versions do not implement --version. Presence is still useful, but
    # do not launch a shell here because it can create the default DPREFIX.
    return DarlingRuntime(executable, lines[0][:160] if lines else "VERSION UNKNOWN")


def host_path_to_darling(path: Path) -> str:
    """Map a host path to Darling's documented /Volumes/SystemRoot mount."""
    resolved = path.expanduser().resolve(strict=True)
    return f"/Volumes/SystemRoot{resolved}"


def build_darling_command(
    runtime: DarlingRuntime, executable: Path, arguments: list[str] | None = None,
) -> list[str]:
    """Build an argv vector without a shell or any binary modification."""
    target = executable.expanduser().resolve(strict=True)
    if not target.is_file():
        raise ValueError(f"macOS executable is not a regular file: {target}")
    return [str(runtime.executable), "shell", host_path_to_darling(target), *(arguments or [])]


def run_darling(
    runtime: DarlingRuntime,
    executable: Path,
    arguments: list[str] | None,
    log_path: Path,
    *,
    prefix: Path | None = None,
) -> int:
    """Run a local macOS program and stream combined output to a private log."""
    argv = build_darling_command(runtime, executable, arguments)
    log_path = log_path.expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    environment = os.environ.copy()
    if prefix is not None:
        resolved_prefix = prefix.expanduser().resolve(strict=True)
        if not resolved_prefix.is_dir():
            raise ValueError(f"Darling prefix is not a directory: {resolved_prefix}")
        environment["DPREFIX"] = str(resolved_prefix)
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        os.chmod(log_path, 0o600)
        log.write(f"Starting Darling process for {Path(executable).resolve()}\n")
        log.flush()
        process = subprocess.Popen(  # nosec B603 -- explicit argv, user-selected program, no shell
            argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            env=environment, start_new_session=True,
        )
        try:
            return process.wait()
        except KeyboardInterrupt:
            # Darling may spawn the application as a child; terminate the
            # session group and reap the process so no orphan remains.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                return process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                return 128 + signal.SIGINT
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait()
