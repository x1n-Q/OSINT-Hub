#!/usr/bin/env python3
"""
OSINT Hub System Checker
Verifies system meets requirements before first run.
"""

import sys
import shutil
from pathlib import Path

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 3.8+ required (found {version.major}.{version.minor})")
        return False

def check_pip():
    if shutil.which("pip3") or shutil.which("pip"):
        print("✓ pip available")
        return True
    print("✗ pip not found")
    return False

def check_git():
    if shutil.which("git"):
        print("✓ git available")
        return True
    print("✗ git not found (required for some tools)")
    return False

def check_display():
    """Check if GUI can run."""
    import os
    if os.environ.get("DISPLAY"):
        print("✓ Display available (GUI supported)")
        return True
    print("⚠ No display detected (use CLI mode)")
    return False

def main():
    print("\n" + "="*50)
    print("OSINT Hub - System Check")
    print("="*50 + "\n")

    checks = [
        ("Python 3.8+", check_python),
        ("pip", check_pip),
        ("git", check_git),
        ("Display", check_display),
    ]

    passed = 0
    for name, check_func in checks:
        print(f"Checking {name}...")
        if check_func():
            passed += 1
        print()

    print("="*50)
    print(f"Result: {passed}/{len(checks)} checks passed")

    if passed == len(checks):
        print("✓ System ready! Run: python3 main.py")
    else:
        print("\nInstall missing dependencies:")
        print("  sudo apt-get install python3 python3-pip git")
        print("\nFor GUI, ensure X11/Wayland is running.")

    print("="*50)

if __name__ == "__main__":
    main()
