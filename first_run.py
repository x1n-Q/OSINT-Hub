#!/usr/bin/env python3
"""
OSINT Hub - First Run Wizard
Guides new users through initial setup.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from osinthub.core.config_manager import ConfigManager
from osinthub.tools.registry import ToolRegistry

def show_welcome():
    print("\n" + "="*60)
    print("   🔍 Welcome to OSINT Hub!")
    print("="*60)
    print("\nOSINT Hub is your all-in-one platform for open source")
    print("intelligence gathering.")
    print("\nLet's set things up...")

def check_dependencies():
    print("\n1. Checking system dependencies...")
    import shutil
    deps = {
        "python3": "Python 3",
        "pip3": "pip package manager",
        "git": "Git version control"
    }

    missing = []
    for cmd, name in deps.items():
        if shutil.which(cmd):
            print(f"   ✓ {name} ({cmd})")
        else:
            print(f"   ✗ {name} ({cmd}) - MISSING")
            missing.append(name)

    if missing:
        print(f"\nPlease install missing dependencies:")
        print(f"  sudo apt-get install {' '.join(deps.keys())}")
        return False
    return True

def install_python_deps():
    print("\n2. Installing Python dependencies...")
    os.system("pip3 install -r requirements.txt")

def setup_config():
    print("\n3. Setting up configuration...")
    cm = ConfigManager()
    cm.save()
    print("   ✓ Configuration file created at ~/.osinthub/config/config.json")

def suggest_tools():
    print("\n4. Recommended starter tools:")
    registry = ToolRegistry()
    starters = ["sherlock", "harvester", "exiftool", "socialscan"]

    for tool_id in starters:
        tool = registry.get_tool(tool_id)
        if tool:
            print(f"   • {tool.icon} {tool.name}")
            print(f"     {tool.description}")

def main():
    show_welcome()

    if not check_dependencies():
        print("\n✗ Setup incomplete. Please install missing dependencies.")
        return

    install_python_deps()
    setup_config()
    suggest_tools()

    print("\n" + "="*60)
    print("✓ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Launch OSINT Hub GUI:")
    print("     python3 main.py")
    print("\n  2. Or use interactive menu:")
    print("     python3 menu.py")
    print("\n  3. Or use full CLI:")
    print("     python3 cli.py --help")
    print("\nHappy hunting! 🔍\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
    except Exception as e:
        print(f"\nSetup error: {e}")
        print("Try running the individual steps manually.")
