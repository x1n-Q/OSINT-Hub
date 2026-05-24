#!/usr/bin/env python3
"""
OSINT Hub System Checker
Verifies system meets requirements before first run.
"""

import shutil
import subprocess
import sys

from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import (
    is_frozen,
    recommended_python_label,
    resolve_runtime_python,
    running_project_venv,
    using_recommended_python,
    venv_python,
)

configure_console()


def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_safe(f"OK Python {version.major}.{version.minor}.{version.micro}")
        if version.minor >= 13:
            print_safe("WARN Python 3.13+ is supported by OSINT Hub itself, but several bundled third-party OSINT tools still break on very new Python versions. Python 3.10 or 3.11 is the safest choice.")
        return True

    print_safe(f"FAIL Python 3.8+ required (found {version.major}.{version.minor})")
    return False


def check_python_recommendation():
    if using_recommended_python():
        print_safe(f"OK Recommended Python {recommended_python_label()} in use")
        return True

    print_safe(f"WARN Recommended Python is {recommended_python_label()} for best tool compatibility")
    return False


def check_pip():
    runtime_python = resolve_runtime_python()
    if runtime_python:
        result = subprocess.run(
            [str(runtime_python), "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print_safe(f"OK pip available via {runtime_python}")
            return True

    if shutil.which("pip3") or shutil.which("pip"):
        print_safe("OK pip available")
        return True

    print_safe("FAIL pip not found")
    return False


def check_git():
    if shutil.which("git"):
        print_safe("OK git available")
        return True

    print_safe("FAIL git not found (required for some tools)")
    return False


def check_project_venv():
    """Check whether the source venv or release tool runtime is ready."""
    runtime_python = resolve_runtime_python()
    if is_frozen():
        if runtime_python:
            print_safe(f"OK Tool runtime available ({runtime_python})")
            return True
        print_safe(
            f"WARN Python {recommended_python_label()} tool runtime not found. "
            "Run OSINT Hub Runtime Setup or bootstrap_runtime.py."
        )
        return False

    venv_executable = venv_python()
    if running_project_venv():
        print_safe(f"OK Project .venv active ({sys.executable})")
        return True

    if venv_executable.exists():
        print_safe(f"WARN Project .venv exists but is not active. Recommended: {venv_executable} main.py")
        return False

    print_safe("WARN Project .venv not found. Run: python bootstrap_env.py")
    return False


def check_display():
    """Check if GUI can run."""
    import os

    if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
        print_safe("OK Display available (GUI supported)")
        return True

    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        print_safe("OK Display available (GUI supported)")
        return True

    try:
        import tkinter

        root = tkinter.Tk()
        root.destroy()
        print_safe("OK Display available (GUI supported)")
        return True
    except Exception:
        print_safe("WARN No display detected (use CLI mode)")
        return False


def main():
    print_safe("\n" + "=" * 50)
    print_safe("OSINT Hub - System Check")
    print_safe("=" * 50 + "\n")

    checks = [
        ("Python 3.8+", check_python),
        (f"Python {recommended_python_label()} recommendation", check_python_recommendation),
        ("pip", check_pip),
        ("git", check_git),
        ("Tool runtime" if is_frozen() else "Project .venv", check_project_venv),
        ("Display", check_display),
    ]

    passed = 0
    for name, check_func in checks:
        print_safe(f"Checking {name}...")
        if check_func():
            passed += 1
        print_safe("")

    print_safe("=" * 50)
    print_safe(f"Result: {passed}/{len(checks)} checks passed")

    if passed == len(checks):
        if is_frozen():
            print_safe("OK System ready! Launch OSINT Hub.exe")
        else:
            print_safe(f"OK System ready! Run: {sys.executable} main.py")
    else:
        print_safe("\nInstall missing dependencies or prepare the project virtual environment first.")
        if is_frozen():
            print_safe("Recommended command: OSINT Hub Runtime Setup.exe")
        else:
            print_safe("Recommended command: python bootstrap_env.py")
        if sys.platform.startswith("win"):
            print_safe("Suggested packages: Python 3 (with pip) and Git for Windows.")
        else:
            print_safe("Suggested packages: python3 python3-pip git")
        print_safe("For GUI mode on Linux, ensure X11 or Wayland is running.")

    print_safe("=" * 50)


if __name__ == "__main__":
    main()
