#!/usr/bin/env python3
"""
OSINT Hub Updater
Checks for and installs updates.
"""

import subprocess
import sys
from pathlib import Path

def check_updates():
    """Check for updates if using git repo."""
    project_root = Path(__file__).parent.parent

    if (project_root / ".git").exists():
        print("Checking for upstream updates...")
        try:
            subprocess.run(["git", "fetch"], cwd=project_root, check=True)
            result = subprocess.run(
                ["git", "status", "-uno"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            if "Your branch is behind" in result.stdout:
                print("Updates available!")
                response = input("Download and install updates? (Y/n): ").lower()
                if response in ('y', 'yes', ''):
                    subprocess.run(["git", "pull"], cwd=project_root, check=True)
                    print("✓ Updated successfully")
                    print("Restart OSINT Hub to use the new version.")
            else:
                print("You're up to date!")
        except Exception as e:
            print(f"Update check failed: {e}")
    else:
        print("Not a git repository. Update manually.")

if __name__ == "__main__":
    check_updates()
