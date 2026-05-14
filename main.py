#!/usr/bin/env python3
"""
OSINT Hub Entry Point
Detects environment and launches appropriate interface.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point - launch GUI by default."""

    # If explicitly requested CLI, use that
    if len(sys.argv) > 1 and sys.argv[1] in ["--cli", "-c", "cli"]:
        from cli import main as cli_main
        cli_main()
        return

    # Try GUI first
    try:
        from osinthub.gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"GUI not available ({e}), falling back to CLI...")
        print("Install GUI dependencies: pip install customtkinter")
        from cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()
