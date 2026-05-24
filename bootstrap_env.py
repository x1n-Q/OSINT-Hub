#!/usr/bin/env python3
"""
Bootstrap a local Python 3.11 virtual environment for OSINT Hub.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import (
    RECOMMENDED_PYTHON,
    find_recommended_python,
    probe_python,
    recommended_python_label,
    requirements_file,
    venv_dir,
    venv_python,
)

configure_console()

def venv_python_version(venv_executable: Path) -> tuple[int, int, int] | None:
    if not venv_executable.exists():
        return None

    probe = probe_python([str(venv_executable)])
    if not probe:
        return None
    return probe[0]


def run_command(command: list[str], cwd: Path) -> None:
    print_safe(f"$ {' '.join(command)}")
    result = subprocess.run(command, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")


def bootstrap(recreate: bool = False, editable: bool = True) -> None:
    root = Path(__file__).resolve().parent
    venv_root = venv_dir(root)
    venv_executable = venv_python(root)

    existing_version = venv_python_version(venv_executable)
    if existing_version and existing_version[:2] != RECOMMENDED_PYTHON:
        if not recreate:
            raise RuntimeError(
                f"Existing .venv uses Python {existing_version[0]}.{existing_version[1]}. "
                f"Run bootstrap_env.py --recreate to rebuild it with Python {recommended_python_label()}."
            )
        shutil.rmtree(venv_root)

    if recreate and venv_root.exists() and not existing_version:
        shutil.rmtree(venv_root)

    python_match = find_recommended_python()
    if not python_match:
        raise RuntimeError(
            f"Python {recommended_python_label()} was not found. Install Python {recommended_python_label()} first, then rerun this script."
        )

    python_command, resolved_python = python_match
    print_safe(f"Using Python {recommended_python_label()}: {resolved_python}")

    if not venv_executable.exists():
        run_command(python_command + ["-m", "venv", str(venv_root)], root)

    locked_requirements = requirements_file(root)
    run_command([str(venv_executable), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], root)
    run_command([str(venv_executable), "-m", "pip", "install", "-r", str(locked_requirements)], root)

    if editable:
        run_command([str(venv_executable), "-m", "pip", "install", "-e", "."], root)

    print_safe("")
    print_safe("Environment ready.")
    if os.name == "nt":
        print_safe(rf"Activate: {venv_root}\Scripts\activate")
        print_safe(rf"Run GUI: {venv_executable} main.py")
        print_safe(rf"Run CLI: {venv_executable} cli.py --help")
    else:
        print_safe(f"Activate: source {venv_root}/bin/activate")
        print_safe(f"Run GUI: {venv_executable} main.py")
        print_safe(f"Run CLI: {venv_executable} cli.py --help")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Python 3.11 virtual environment for OSINT Hub.")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate .venv if it already exists.")
    parser.add_argument("--no-editable", action="store_true", help="Skip 'pip install -e .' after dependency install.")
    args = parser.parse_args()

    bootstrap(recreate=args.recreate, editable=not args.no_editable)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_safe("\nBootstrap cancelled.")
        raise SystemExit(1)
    except Exception as exc:
        print_safe(f"\nBootstrap failed: {exc}")
        raise SystemExit(1)
