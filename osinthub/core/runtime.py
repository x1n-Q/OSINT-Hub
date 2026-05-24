"""
Runtime helpers for source checkouts, virtual environments, and frozen builds.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path


RECOMMENDED_PYTHON = (3, 11)


def is_frozen() -> bool:
    """Return True when running from a bundled executable."""
    return bool(getattr(sys, "frozen", False))


def recommended_python_label() -> str:
    return f"{RECOMMENDED_PYTHON[0]}.{RECOMMENDED_PYTHON[1]}"


def project_root(anchor: Path | None = None) -> Path:
    if anchor:
        return anchor.resolve()
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def bundle_root() -> Path:
    """Return the directory containing bundled application resources."""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return project_root()


def venv_dir(root: Path | None = None) -> Path:
    return project_root(root) / ".venv"


def venv_python(root: Path | None = None) -> Path:
    venv_root = venv_dir(root)
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def managed_runtime_root(home: Path | None = None) -> Path:
    from osinthub.core.paths import get_osinthub_home

    base = Path(home) if home else get_osinthub_home()
    return base / "runtime"


def managed_runtime_dir(home: Path | None = None) -> Path:
    return managed_runtime_root(home) / ".venv"


def managed_runtime_python(home: Path | None = None) -> Path:
    runtime_root = managed_runtime_dir(home)
    if os.name == "nt":
        return runtime_root / "Scripts" / "python.exe"
    return runtime_root / "bin" / "python"


def python_scripts_dir(python_executable: Path) -> Path:
    return python_executable.resolve().parent


def python_is_virtualenv(python_executable: Path) -> bool:
    try:
        return (python_scripts_dir(python_executable).parent / "pyvenv.cfg").exists()
    except Exception:
        return False


def in_virtualenv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def running_project_venv(root: Path | None = None) -> bool:
    expected = venv_python(root)
    try:
        return expected.exists() and Path(sys.executable).resolve() == expected.resolve()
    except Exception:
        return False


def using_recommended_python() -> bool:
    version = sys.version_info
    return (version.major, version.minor) == RECOMMENDED_PYTHON


def requirements_file(root: Path | None = None) -> Path:
    base = project_root(root)
    pinned = base / "requirements-py311.txt"
    if pinned.exists():
        return pinned
    return base / "requirements.txt"


def probe_python(command: list[str]) -> tuple[tuple[int, int, int], str] | None:
    """Return version and resolved executable for a python command."""
    try:
        result = subprocess.run(
            command + [
                "-c",
                "import sys; print(sys.version_info[0], sys.version_info[1], sys.version_info[2]); print(sys.executable)",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    try:
        major, minor, micro = (int(part) for part in lines[0].split())
    except Exception:
        return None

    return (major, minor, micro), lines[1]


@lru_cache(maxsize=1)
def find_recommended_python() -> tuple[list[str], str] | None:
    preferred = []

    if (sys.version_info.major, sys.version_info.minor) == RECOMMENDED_PYTHON and not is_frozen():
        preferred.append(([sys.executable], sys.executable))

    local_app_data = os.environ.get("LOCALAPPDATA")
    common_candidates = [
        ["python3.11"],
        ["python311"],
        ["python3"],
        ["python"],
    ]
    if os.name == "nt":
        common_candidates.insert(0, ["py", "-3.11"])
        if local_app_data:
            common_candidates.append([str(Path(local_app_data) / "Programs" / "Python" / "Python311" / "python.exe")])
        common_candidates.append([r"C:\Python311\python.exe"])

    seen = set()
    for command, executable in preferred:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            probe = probe_python(command)
            if probe and probe[0][:2] == RECOMMENDED_PYTHON:
                return command, executable

    for command in common_candidates:
        key = tuple(command)
        if key in seen:
            continue
        seen.add(key)

        probe = probe_python(command)
        if probe and probe[0][:2] == RECOMMENDED_PYTHON:
            return command, probe[1]

    return None


@lru_cache(maxsize=4)
def resolve_runtime_python(root: Path | None = None) -> Path | None:
    """Return the preferred real Python interpreter for tool installs and script execution."""
    candidates: list[Path] = []

    def add_candidate(candidate: str | Path | None) -> None:
        if not candidate:
            return
        path = Path(candidate).expanduser()
        if not path.is_absolute():
            try:
                resolved = shutil.which(str(path))
                if not resolved:
                    return
                path = Path(resolved)
            except Exception:
                return
        try:
            resolved_path = path.resolve()
        except Exception:
            resolved_path = path
        if resolved_path.exists() and resolved_path not in candidates:
            candidates.append(resolved_path)

    add_candidate(os.environ.get("OSINTHUB_RUNTIME_PYTHON"))
    add_candidate(venv_python(root))
    add_candidate(managed_runtime_python())

    if not is_frozen():
        add_candidate(sys.executable)

    recommended = find_recommended_python()
    if recommended:
        add_candidate(recommended[1])

    for command_name in ("python3.11", "python3", "python"):
        add_candidate(shutil.which(command_name))

    if os.name == "nt":
        for command in (["py", "-3.11"], ["py", "-3"]):
            probe = probe_python(command)
            if probe:
                add_candidate(probe[1])

    return candidates[0] if candidates else None


@lru_cache(maxsize=4)
def runtime_scripts_dir(root: Path | None = None) -> Path | None:
    runtime_python = resolve_runtime_python(root)
    if not runtime_python:
        return None
    return python_scripts_dir(runtime_python)


def maybe_reexec_in_project_venv(root: Path | None = None, argv: list[str] | None = None) -> bool:
    """Re-exec the current command inside the project venv if it exists."""
    if is_frozen():
        return False

    target_python = venv_python(root)
    if not target_python.exists():
        return False

    if running_project_venv(root):
        return False

    command_argv = argv or [str(path) for path in sys.argv]
    os.execv(str(target_python), [str(target_python), *command_argv])
    return True
