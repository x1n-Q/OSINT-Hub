#!/usr/bin/env python3
"""
OSINT Hub - Complete Setup & Installation
One-command setup for beginners.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from osinthub.core.console import configure_console, print_safe
from osinthub.core.paths import get_osinthub_home
from osinthub.core.runtime import recommended_python_label, venv_python

configure_console()


def print_step(step, description):
    print_safe(f"\n{'=' * 60}")
    print_safe(f"Step {step}: {description}")
    print_safe("=" * 60)


def run_cmd(cmd, description):
    print_safe(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode == 0:
        print_safe(f"OK {description}")
        return True

    print_safe("FAIL")
    return False


def main():
    print_step(1, "System Check")
    print_safe("Verifying Python, pip, git...")

    if shutil.which("python3") or shutil.which("python"):
        print_safe("OK Python 3 found")
    else:
        print_safe("FAIL Python 3 not found!")
        return

    if shutil.which("pip3") or shutil.which("pip"):
        print_safe("OK pip found")
    else:
        print_safe("FAIL pip not found!")
        return

    if shutil.which("git"):
        print_safe("OK git found")
    else:
        print_safe("FAIL git not found!")
        return

    if sys.version_info.minor >= 13:
        print_safe("WARN Python 3.13+ may break some bundled OSINT tools. Python 3.10 or 3.11 is recommended for best compatibility.")

    print_step(2, f"Create Python {recommended_python_label()} Virtual Environment")
    if not run_cmd([sys.executable, "bootstrap_env.py"], "Project virtual environment created"):
        return

    print_step(3, "Create Directories")
    data_home = get_osinthub_home()
    os.makedirs(data_home / "config", exist_ok=True)
    os.makedirs(data_home / "results", exist_ok=True)
    os.makedirs(data_home / "tools", exist_ok=True)
    print_safe("OK Directories created")

    print_step(4, "Make Scripts Executable")
    if os.name == "posix":
        run_cmd(
            ["chmod", "+x", "main.py", "cli.py", "menu.py", "launch.sh", "first_run.py", "test_system.py"],
            "Scripts made executable",
        )
    else:
        print_safe("OK Skipped (not required on Windows)")

    print_step(5, "Verify Installation")
    project_python = venv_python()
    run_cmd([str(project_python), "test_system.py"], "System verification complete")

    print_safe("\n" + "=" * 60)
    print_safe("INSTALLATION COMPLETE!")
    print_safe("=" * 60)

    print_safe("\nWhat's next?")
    print_safe(f"\n1. First run wizard:\n   {project_python} first_run.py")
    print_safe(f"\n2. Interactive menu:\n   {project_python} menu.py")
    print_safe(f"\n3. Full GUI:\n   {project_python} main.py")
    print_safe(f"\n4. Command line:\n   {project_python} cli.py --help")

    response = input("\nWould you like to launch the First Run Wizard now? (Y/n): ").lower()
    if response in ("y", "yes", ""):
        subprocess.run([str(project_python), "first_run.py"], check=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_safe("\n\nSetup cancelled.")
    except Exception as e:
        print_safe(f"\nError during setup: {e}")
        print_safe("Please check the error above and try again.")
