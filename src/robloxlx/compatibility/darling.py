"""Discovery and process management for a user-installed Darling runtime.

The launcher never initializes or edits a DPREFIX. The caller must choose an
existing prefix; Darling may initialize its default prefix when first started.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import platform
import plistlib
import shutil
import signal
import struct
import subprocess  # nosec B404 -- fixed probes and explicit, shell-free argv
import tempfile
from robloxlx.graphics.vulkan import select_hardware_vulkan_environment


@dataclass(frozen=True)
class DarlingRuntime:
    executable: Path
    version: str


@dataclass(frozen=True)
class DarlingSmokeResult:
    passed: bool
    detail: str


def detect_darling() -> DarlingRuntime | None:
    """Locate Darling without executing it or initializing a default prefix."""
    resolved = shutil.which("darling")
    if not resolved:
        return None
    executable = Path(resolved).resolve()
    # Darling's launcher may create a prefix and perform privileged namespace
    # setup even for unsupported arguments, so discovery must remain a PATH
    # lookup. The isolated darling-test command performs the first execution.
    helper = executable.with_name("darlingserver")
    if not helper.is_file():
        version = "INCOMPLETE (darlingserver NOT FOUND; version not queried)"
    else:
        version = "VERSION NOT QUERIED (runtime not started)"
    return DarlingRuntime(executable, version)


def host_path_to_darling(path: Path) -> str:
    """Map a host path to Darling's documented /Volumes/SystemRoot mount."""
    resolved = path.expanduser().resolve(strict=True)
    return f"/Volumes/SystemRoot{resolved}"


def _macho_architectures(path: Path) -> set[str]:
    """Read Mach-O headers only; require an executable slice for supported CPUs."""
    with path.open("rb") as source:
        header = source.read(4096)
        file_size = path.stat().st_size
    if len(header) < 8:
        raise ValueError(f"not a complete Mach-O executable: {path}")
    thin = {
        b"\xcf\xfa\xed\xfe": "<",  # MH_MAGIC_64
        b"\xfe\xed\xfa\xcf": ">",
    }
    if header[:4] in thin:
        endian = thin[header[:4]]
        cpu_type, = struct.unpack_from(f"{endian}I", header, 4)
        file_type, = struct.unpack_from(f"{endian}I", header, 12)
        if file_type != 2:  # MH_EXECUTE
            raise ValueError(f"Mach-O file is not an executable image: {path}")
        return {"x86_64"} if cpu_type == 0x01000007 else {"arm64"} if cpu_type == 0x0100000C else set()
    fat = {
        b"\xca\xfe\xba\xbe": (">", 20), b"\xca\xfe\xba\xbf": (">", 32),
        b"\xbe\xba\xfe\xca": ("<", 20), b"\xbf\xba\xfe\xca": ("<", 32),
    }
    if header[:4] not in fat:
        raise ValueError(f"not a 64-bit Mach-O executable: {path}")
    endian, entry_size = fat[header[:4]]
    count, = struct.unpack_from(f"{endian}I", header, 4)
    if count < 1 or count > 64 or 8 + count * entry_size > len(header):
        raise ValueError(f"invalid universal Mach-O header: {path}")
    architectures: set[str] = set()
    with path.open("rb") as source:
        for index in range(count):
            offset = 8 + index * entry_size
            cpu_type, = struct.unpack_from(f"{endian}I", header, offset)
            if entry_size == 20:
                slice_offset, slice_size = struct.unpack_from(f"{endian}II", header, offset + 8)
            else:
                slice_offset, slice_size = struct.unpack_from(f"{endian}QQ", header, offset + 8)
            if slice_size < 32 or slice_offset + slice_size > file_size:
                raise ValueError(f"invalid universal Mach-O slice bounds: {path}")
            if cpu_type not in (0x01000007, 0x0100000C):
                continue
            source.seek(slice_offset)
            image = source.read(32)
            image_endian = thin.get(image[:4])
            if not image_endian:
                raise ValueError(f"invalid universal Mach-O executable slice: {path}")
            image_cpu, = struct.unpack_from(f"{image_endian}I", image, 4)
            image_type, = struct.unpack_from(f"{image_endian}I", image, 12)
            if image_cpu != cpu_type or image_type != 2:
                raise ValueError(f"universal Mach-O slice header mismatch: {path}")
            architectures.add("x86_64" if cpu_type == 0x01000007 else "arm64")
    return architectures


def resolve_macos_executable(program: Path) -> Path:
    """Resolve a Mach-O binary or its .app bundle and check host architecture."""
    target = program.expanduser().resolve(strict=True)
    if target.is_dir():
        if target.suffix != ".app":
            raise ValueError(f"directory is not a macOS .app bundle: {target}")
        bundle = target
        contents = bundle / "Contents"
        try:
            with (contents / "Info.plist").open("rb") as source:
                info = plistlib.load(source)
        except (OSError, plistlib.InvalidFileException) as exc:
            raise ValueError(f"cannot read app bundle Info.plist: {exc}") from exc
        executable_name = info.get("CFBundleExecutable") if isinstance(info, dict) else None
        if not isinstance(executable_name, str) or not executable_name or Path(executable_name).name != executable_name:
            raise ValueError("app bundle Info.plist has no safe CFBundleExecutable name")
        target = (contents / "MacOS" / executable_name).resolve(strict=True)
        if not target.is_relative_to(bundle):
            raise ValueError("app bundle executable resolves outside the .app bundle")
    if not target.is_file():
        raise ValueError(f"macOS executable is not a regular file: {target}")
    if not os.access(target, os.X_OK):
        raise ValueError(f"macOS executable is not marked executable: {target}")
    architectures = _macho_architectures(target)
    expected = "arm64" if platform.machine().lower() in ("aarch64", "arm64") else "x86_64"
    if expected not in architectures:
        found = ", ".join(sorted(architectures)) if architectures else "no supported 64-bit Mach-O architecture"
        raise ValueError(f"executable architecture mismatch: host {expected}, file has {found}")
    return target


def build_darling_command(
    runtime: DarlingRuntime, executable: Path, arguments: list[str] | None = None,
) -> list[str]:
    """Build an argv vector without a shell or any binary modification."""
    target = resolve_macos_executable(executable)
    return [str(runtime.executable), "shell", host_path_to_darling(target), *(arguments or [])]


def _stop_process_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def test_darling_runtime(log_path: Path | None = None) -> DarlingSmokeResult:
    """Compile and run the independent libSystem write/exit probe."""
    return _test_fixture("macho_hello.s", "ROBLOXLX_MACHO_OK", "_start", [], log_path)


def test_metal_runtime(log_path: Path | None = None, *, driver: Path | None = None,
                       library: Path | None = None) -> DarlingSmokeResult:
    """Exercise real Metal buffer commands; does not prove window presentation."""
    return _test_fixture("macho_metal.c", "ROBLOXLX_METAL_BUFFER_OK", "_main", ["Metal"], log_path,
                         vulkan_driver=driver, metal_library=library)


def test_network_runtime(log_path: Path | None = None) -> DarlingSmokeResult:
    """Check real Darwin DNS and TCP loopback without any Roblox traffic."""
    return _test_fixture("macho_network.c", "ROBLOXLX_NETWORK_OK", "_main", [], log_path)


def _test_fixture(source_name: str, marker: str, entry: str, frameworks: list[str],
                  log_path: Path | None, *, vulkan_driver: Path | None = None,
                  metal_library: Path | None = None) -> DarlingSmokeResult:
    runtime = detect_darling()
    if runtime is None:
        return DarlingSmokeResult(False, "Darling NOT FOUND; no process started")
    if platform.machine().lower() not in ("x86_64", "amd64"):
        return DarlingSmokeResult(False, f"Mach-O probe supports x86_64 only; host is {platform.machine()}")
    clang, linker = shutil.which("clang"), shutil.which("ld64.lld")
    if not clang or not linker:
        return DarlingSmokeResult(False, "clang and ld64.lld are required to build the local Mach-O test")
    sysroot = runtime.executable.parent.parent / "libexec/darling"
    if not (sysroot / "usr/lib/libSystem.B.dylib").is_file():
        return DarlingSmokeResult(False, f"Darling libSystem runtime NOT FOUND under {sysroot}")
    source = Path(__file__).parent / "fixtures" / source_name
    with tempfile.TemporaryDirectory(prefix="robloxlx-darling-smoke-") as folder:
        root = Path(folder)
        obj, executable = root / "hello.o", root / "hello"
        try:
            overrides = select_hardware_vulkan_environment(vulkan_driver) if "Metal" in frameworks else {}
            compile_result = subprocess.run(  # nosec B603 -- fixed local fixture and argv, no shell
                [clang, "-target", "x86_64-apple-macos10.15", "-c", str(source), "-o", str(obj)],
                capture_output=True, text=True, timeout=20, check=False,
            )
            if compile_result.returncode:
                return DarlingSmokeResult(False, f"Clang failed: {compile_result.stderr.strip()[:300]}")
            framework_args = ["-F", str(sysroot / "System/Library/Frameworks"), "-lobjc"] if frameworks else []
            for framework in frameworks:
                if framework == "Metal" and metal_library is not None:
                    replacement = metal_library.expanduser().resolve(strict=True)
                    if not replacement.is_file():
                        raise ValueError(f"Metal implementation library is not a file: {replacement}")
                    framework_args.append(str(replacement))
                else:
                    framework_args.extend(["-framework", framework])
            link_result = subprocess.run(  # nosec B603 -- fixed local object and argv, no shell
                [linker, "-arch", "x86_64", "-platform_version", "macos", "11.0", "11.0",
                 "-e", entry, "-syslibroot", str(sysroot), "-lSystem", *framework_args,
                 "-o", str(executable), str(obj)],
                capture_output=True, text=True, timeout=20, check=False,
            )
            if link_result.returncode:
                return DarlingSmokeResult(False, f"ld64.lld failed: {link_result.stderr.strip()[:300]}")
            log = log_path if log_path is not None else root / "darling.log"
            return _run_independent_probe(runtime, executable, marker, log, overrides)
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            return DarlingSmokeResult(False, f"Darling smoke test failed: {exc}")


def test_window_runtime(executable: Path, log_path: Path, *, driver: Path | None = None,
                        wsi: str = "wayland") -> DarlingSmokeResult:
    return _test_window_probe(executable, log_path, driver=driver, wsi=wsi,
                             marker="ROBLOXLX_MACOS_VULKAN_WINDOW_OK")


def test_public_window_runtime(executable: Path, log_path: Path, *, driver: Path | None = None,
                               wsi: str = "wayland") -> DarlingSmokeResult:
    """Test the separately linked limited public window/layer implementation."""
    return _test_window_probe(executable, log_path, driver=driver, wsi=wsi,
                             marker="ROBLOXLX_PUBLIC_WINDOW_OK")


def _test_window_probe(executable: Path, log_path: Path, *, driver: Path | None = None,
                        wsi: str = "wayland", marker: str) -> DarlingSmokeResult:
    """Run a source-built independent WSI fixture, not a Roblox executable."""
    if wsi not in ("wayland", "x11"):
        return DarlingSmokeResult(False, "WSI must be wayland or x11")
    runtime = detect_darling()
    if runtime is None or runtime.version.startswith("INCOMPLETE"):
        return DarlingSmokeResult(False, "Complete Darling runtime NOT FOUND")
    try:
        target = resolve_macos_executable(executable)
        overrides = select_hardware_vulkan_environment(driver)
        overrides.update({"ROBLOXLX_METAL_WSI": wsi, "SDL_VIDEODRIVER": wsi})
        return _run_independent_probe(runtime, target, marker, log_path, overrides)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return DarlingSmokeResult(False, f"Darling WSI test failed: {exc}")


def _run_independent_probe(runtime: DarlingRuntime, executable: Path, marker: str,
                           log_path: Path, overrides: dict[str, str]) -> DarlingSmokeResult:
    # Keep the prefix outside the disposable build directory: Darling
    # creates root-owned overlay files which cannot be removed safely
    # by an unprivileged test. Preserve them for diagnosis, never sudo-rm.
    prefix_root = Path(tempfile.mkdtemp(prefix="robloxlx-darling-prefix-"))
    prefix = prefix_root / "dprefix"
    environment = os.environ.copy()
    environment.update(overrides)
    environment["DPREFIX"] = str(prefix)
    # An empty pre-created directory makes Darling skip setupPrefix().
    # Initialize only this isolated test prefix through its own launcher.
    initialized = subprocess.run(  # nosec B603 -- fixed launcher command, isolated probe prefix
        [str(runtime.executable), "--version"], env=environment,
        capture_output=True, text=True, timeout=10, check=False,
    )
    if initialized.returncode or not prefix.is_dir():
        return DarlingSmokeResult(False, f"Darling probe prefix initialization failed: {initialized.stderr.strip()}")
    log = log_path
    log_offset = log.stat().st_size if log.exists() else 0
    try:
        status = run_darling(runtime, executable, [], log, prefix=prefix, timeout=30,
                             environment_overrides=overrides)
    finally:
        try:
            stopped = subprocess.run(  # nosec B603 -- stops only the server belonging to the isolated probe prefix
                [str(runtime.executable), "shutdown"], env=environment,
                capture_output=True, text=True, timeout=5, check=False,
            )
            shutdown_detail = f"exit {stopped.returncode}: {stopped.stderr.strip()}"
        except (OSError, subprocess.TimeoutExpired) as exc:
            shutdown_detail = f"UNKNOWN: {exc}"
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"Probe shutdown {shutdown_detail}; retained prefix: {prefix}\n")
    output = log.read_bytes()[log_offset:].decode("utf-8", errors="replace") if log.exists() else ""
    if status != 0 or marker not in output:
        tail = "\n".join(output.splitlines()[-12:]).strip()
        detail = f"macOS API probe failed (exit {status})"
        if tail:
            detail += f"; Darling output:\n{tail}"
        return DarlingSmokeResult(False, detail)
    return DarlingSmokeResult(True, f"Independent macOS executable returned {marker}")

def run_darling(
    runtime: DarlingRuntime,
    executable: Path,
    arguments: list[str] | None,
    log_path: Path,
    *,
    prefix: Path | None = None,
    timeout: float | None = None,
    environment_overrides: dict[str, str] | None = None,
) -> int:
    """Run a local macOS program and stream combined output to a private log."""
    argv = build_darling_command(runtime, executable, arguments)
    log_path = log_path.expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    environment = os.environ.copy()
    if environment_overrides:
        environment.update(environment_overrides)
    if prefix is not None:
        resolved_prefix = prefix.expanduser().resolve(strict=True)
        if not resolved_prefix.is_dir():
            raise ValueError(f"Darling prefix is not a directory: {resolved_prefix}")
        environment["DPREFIX"] = str(resolved_prefix)
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        os.chmod(log_path, 0o600)
        log.write(f"Starting Darling process for {Path(executable).resolve()}\n")
        if environment.get("VK_DRIVER_FILES"):
            log.write(f"Vulkan driver: {environment['VK_DRIVER_FILES']}\n")
        log.flush()
        process = subprocess.Popen(  # nosec B603 -- explicit argv, user-selected program, no shell
            argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            env=environment, start_new_session=True,
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            log.write(f"Darling process timed out after {timeout:g}s; terminating process group\n")
            log.flush()
            _stop_process_group(process)
            return 124
        except KeyboardInterrupt:
            # Darling may spawn the application as a child; terminate the
            # session group and reap the process so no orphan remains.
            _stop_process_group(process)
            return 128 + signal.SIGINT
        finally:
            if process.poll() is None:
                _stop_process_group(process)
