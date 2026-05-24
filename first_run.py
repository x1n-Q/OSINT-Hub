#!/usr/bin/env python3
"""
OSINT Hub - First Run Wizard
Guides new users through initial setup.
"""

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from osinthub.core.config_manager import ConfigManager
from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import recommended_python_label, running_project_venv, venv_python
from osinthub.tools.registry import ToolRegistry

configure_console()


def show_welcome():
    print_safe("\n" + "=" * 60)
    print_safe("Welcome to OSINT Hub!")
    print_safe("=" * 60)
    print_safe("\nOSINT Hub is your all-in-one platform for open source")
    print_safe("intelligence gathering.")
    print_safe("\nLet's set things up...")


def check_dependencies():
    print_safe("\n1. Checking system dependencies...")

    has_python = shutil.which("python3") or shutil.which("python")
    has_pip = shutil.which("pip3") or shutil.which("pip")
    has_git = shutil.which("git")

    if has_python:
        print_safe(f"   OK Python 3 ({has_python})")
    else:
        print_safe("   FAIL Python 3 - missing")

    if has_pip:
        print_safe(f"   OK pip ({has_pip})")
    else:
        print_safe("   FAIL pip - missing")

    if has_git:
        print_safe(f"   OK Git ({has_git})")
    else:
        print_safe("   FAIL Git - missing")

    missing = []
    if not has_python:
        missing.append("Python 3")
    if not has_pip:
        missing.append("pip")
    if not has_git:
        missing.append("Git")

    if missing:
        print_safe("\nPlease install missing dependencies:")
        if sys.platform.startswith("win"):
            print_safe("  Install Python (with pip) and Git for Windows.")
        else:
            print_safe("  Install python3, python3-pip, and git with your package manager.")
        return False

    if sys.version_info.minor >= 13:
        print_safe("   WARN Python 3.13+ can break older OSINT tool dependencies. Python 3.10 or 3.11 is recommended for best tool compatibility.")
    if not running_project_venv():
        print_safe(f"   WARN Project .venv is not active yet. This wizard will prepare a Python {recommended_python_label()} environment.")

    return True


def install_python_deps():
    print_safe("\n2. Preparing project virtual environment...")
    result = subprocess.run([sys.executable, "bootstrap_env.py"], check=False)
    if result.returncode == 0:
        print_safe("   OK Project virtual environment prepared")
        return True

    print_safe("   FAIL Virtual environment setup failed")
    return False


def setup_config():
    print_safe("\n3. Setting up configuration...")
    config_manager = ConfigManager()
    config_manager.save()
    print_safe(f"   OK Configuration file created at {config_manager.config_file}")


def suggest_tools():
    print_safe("\n4. Recommended starter tools:")
    registry = ToolRegistry()
    starters = ["sherlock", "harvester", "socialscan", "instaloader"]

    for tool_id in starters:
        tool = registry.get_tool(tool_id)
        if tool:
            print_safe(f"   * {tool.icon} {tool.name}")
            print_safe(f"     {tool.description}")


def main():
    show_welcome()

    if not check_dependencies():
        print_safe("\nSetup incomplete. Please install missing dependencies.")
        return

    if not install_python_deps():
        print_safe("\nSetup incomplete. Please install Python 3.11 and rerun bootstrap_env.py.")
        return
    setup_config()
    suggest_tools()

    print_safe("\n" + "=" * 60)
    print_safe("Setup complete!")
    print_safe("=" * 60)
    venv_executable = venv_python()
    print_safe("\nNext steps:")
    print_safe(f"  1. Launch OSINT Hub GUI:\n     {venv_executable} main.py")
    print_safe(f"\n  2. Or use interactive menu:\n     {venv_executable} menu.py")
    print_safe(f"\n  3. Or use full CLI:\n     {venv_executable} cli.py --help")
    print_safe("\nHappy hunting!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_safe("\nSetup cancelled.")
    except Exception as e:
        print_safe(f"\nSetup error: {e}")
        print_safe("Try running the individual steps manually.")
