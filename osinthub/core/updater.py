#!/usr/bin/env python3
"""
OSINT Hub Updater
Checks for and installs updates.
"""

from __future__ import annotations

import subprocess

from osinthub.core.runtime import is_frozen, project_root


def check_updates():
    """Check for updates when running from a git checkout."""
    if is_frozen():
        print("Bundled release detected. Download a new OSINT Hub release to update this app.")
        return

    repo_root = project_root()
    if not (repo_root / ".git").exists():
        print("Not a git repository. Update manually.")
        return

    print("Checking for upstream updates...")
    try:
        subprocess.run(["git", "fetch"], cwd=repo_root, check=True)
        result = subprocess.run(
            ["git", "status", "-uno"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if "Your branch is behind" in result.stdout:
            print("Updates available!")
            response = input("Download and install updates? (Y/n): ").lower()
            if response in ("y", "yes", ""):
                subprocess.run(["git", "pull"], cwd=repo_root, check=True)
                print("Updated successfully")
                print("Restart OSINT Hub to use the new version.")
        else:
            print("You're up to date!")
    except Exception as exc:
        print(f"Update check failed: {exc}")


if __name__ == "__main__":
    check_updates()
