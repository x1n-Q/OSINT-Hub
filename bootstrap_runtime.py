#!/usr/bin/env python3
"""
Bootstrap the managed Python runtime used by release builds.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import (
    RECOMMENDED_PYTHON,
    find_recommended_python,
    managed_runtime_dir,
    managed_runtime_python,
    probe_python,
    recommended_python_label,
)

configure_console()


def runtime_python_version(runtime_executable: Path) -> tuple[int, int, int] | None:
    if not runtime_executable.exists():
        return None

    probe = probe_python([str(runtime_executable)])
    if not probe:
        return None
    return probe[0]


def run_command(command: list[str], cwd: Path) -> None:
    print_safe(f"$ {' '.join(command)}")
    result = subprocess.run(command, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")


def bootstrap(recreate: bool = False) -> None:
    runtime_root = managed_runtime_dir()
    runtime_home = runtime_root.parent
    runtime_home.mkdir(parents=True, exist_ok=True)
    runtime_executable = managed_runtime_python()

    existing_version = runtime_python_version(runtime_executable)
    if existing_version and existing_version[:2] != RECOMMENDED_PYTHON:
        if not recreate:
            raise RuntimeError(
                f"Existing runtime uses Python {existing_version[0]}.{existing_version[1]}. "
                f"Rerun with --recreate to rebuild it with Python {recommended_python_label()}."
            )
        shutil.rmtree(runtime_root)

    if recreate and runtime_root.exists() and not existing_version:
        shutil.rmtree(runtime_root)

    python_match = find_recommended_python()
    if not python_match:
        raise RuntimeError(
            f"Python {recommended_python_label()} was not found. Install Python {recommended_python_label()} first, then rerun this setup."
        )

    python_command, resolved_python = python_match
    print_safe(f"Using Python {recommended_python_label()}: {resolved_python}")

    if not runtime_executable.exists():
        run_command(python_command + ["-m", "venv", str(runtime_root)], runtime_home)

    run_command([str(runtime_executable), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], runtime_home)

    print_safe("")
    print_safe("Managed tool runtime ready.")
    print_safe(f"Python: {runtime_executable}")
    print_safe("OSINT Hub can now install and run Python-based tools from the app or the release build.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the managed Python 3.11 runtime used by OSINT Hub release builds.")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate the managed runtime if it already exists.")
    args = parser.parse_args()

    bootstrap(recreate=args.recreate)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_safe("\nRuntime setup cancelled.")
        raise SystemExit(1)
    except Exception as exc:
        print_safe(f"\nRuntime setup failed: {exc}")
        raise SystemExit(1)
