#!/usr/bin/env python3
"""
OSINT Hub Entry Point
Detects environment and launches appropriate interface.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from osinthub.core.runtime import maybe_reexec_in_project_venv

if Path(sys.argv[0]).stem.lower() in {"main", "osinthub", "osinthub-gui"}:
    maybe_reexec_in_project_venv(PROJECT_ROOT)

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
    except Exception as e:
        error_text = str(e).lower()
        if e.__class__.__name__ == "TclError" or "display" in error_text:
            print(f"GUI could not start ({e}), falling back to CLI...")
            from cli import main as cli_main
            cli_main()
            return
        raise

if __name__ == "__main__":
    main()
