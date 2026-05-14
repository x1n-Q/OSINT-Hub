#!/usr/bin/env python3
"""
OSINT Hub - Complete Setup & Installation
One-command setup for beginners.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"Step {step}: {description}")
    print('='*60)

def run_cmd(cmd, description):
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ Failed")
        return False

def main():
    print_step(1, "System Check")
    print("Verifying Python, pip, git...")

    if not os.system("which python3 > /dev/null 2>&1"):
        print("✓ Python 3 found")
    else:
        print("✗ Python 3 not found! Install: sudo apt-get install python3")
        return

    if not os.system("which pip3 > /dev/null 2>&1"):
        print("✓ pip3 found")
    else:
        print("✗ pip3 not found! Install: sudo apt-get install python3-pip")
        return

    if not os.system("which git > /dev/null 2>&1"):
        print("✓ git found")
    else:
        print("✗ git not found! Install: sudo apt-get install git")
        return

    print_step(2, "Install Python Dependencies")
    if not run_cmd("pip3 install -r requirements.txt", "Dependencies installed"):
        print("Trying with --break-system-packages flag...")
        run_cmd("pip3 install --break-system-packages -r requirements.txt", "Dependencies installed")

    print_step(3, "Create Directories")
    os.makedirs(Path.home() / ".osinthub" / "config", exist_ok=True)
    os.makedirs(Path.home() / ".osinthub" / "results", exist_ok=True)
    os.makedirs(Path.home() / ".osinthub" / "tools", exist_ok=True)
    print("✓ Directories created")

    print_step(4, "Make Scripts Executable")
    run_cmd("chmod +x main.py cli.py menu.py launch.sh first_run.py test_system.py", "Scripts made executable")

    print_step(5, "Verify Installation")
    run_cmd("python3 test_system.py", "System verification complete")

    print("\n" + "="*60)
    print("✓ INSTALLATION COMPLETE!")
    print("="*60)

    print("\nWhat's next?")
    print("\n1️⃣  FIRST RUN WIZARD (Recommended for beginners):")
    print("   python3 first_run.py")
    print("   This will guide you through initial setup")

    print("\n2️⃣  INTERACTIVE MENU (Easy to use):")
    print("   python3 menu.py")
    print("   Numbered menu - just pick options")

    print("\n3️⃣  FULL GUI (Modern interface):")
    print("   python3 main.py")
    print("   Click-based graphical application")

    print("\n4️⃣  COMMAND LINE (Power users):")
    print("   python3 cli.py --help")
    print("   Full control with commands")

    print("\n5️⃣  QUICK START (Install recommended tools):")
    print("   After launching GUI, choose option 5 from menu")
    print("   OR run: python3 menu.py and choose option 5")

    print("\n" + "="*60)
    print("GETTING HELP")
    print("="*60)
    print("📖 README.md          - Full documentation")
    print("🔧 cli.py --help      - CLI command help")
    print("\n💡 Tip: Start with 'python3 menu.py' for guided experience")

    response = input("\nWould you like to launch the First Run Wizard now? (Y/n): ").lower()
    if response in ('y', 'yes', ''):
        os.system("python3 first_run.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\nError during setup: {e}")
        print("Please check the error above and try again.")
