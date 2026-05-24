#!/usr/bin/env python3
"""
Generate a full OSINT Hub tool audit report for local QA.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import maybe_reexec_in_project_venv
from osinthub.core.tool_audit import build_audit_report, save_audit_report, summarize_audit_report

if Path(sys.argv[0]).stem.lower() in {"tool_audit", "osinthub-audit"}:
    maybe_reexec_in_project_venv(PROJECT_ROOT)

configure_console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local OSINT Hub tool audit report.")
    parser.add_argument(
        "--output",
        "-o",
        default="tool_audit_latest.json",
        help="Path to the JSON report file.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Skip the console summary and only write the JSON report.",
    )
    args = parser.parse_args()

    report = build_audit_report()
    output_path = save_audit_report(report, args.output)

    if not args.quiet:
        for line in summarize_audit_report(report):
            print_safe(line)
        print_safe("")
        print_safe(f"Saved JSON report to {output_path}")


if __name__ == "__main__":
    main()
