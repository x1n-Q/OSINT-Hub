"""
Helpers for generating portable OSINT Hub tool audit reports.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from osinthub.core.runtime import recommended_python_label, resolve_runtime_python
from osinthub.core.tool_manager import ToolManager


def build_audit_report(tool_manager: ToolManager | None = None) -> dict:
    """Build a complete audit report for all registered tools."""
    manager = tool_manager or ToolManager()
    tools = manager.audit_tools()
    runtime_python = resolve_runtime_python()

    status_counts: dict[str, int] = {}
    for tool in tools:
        status = tool["availability"]
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": manager.current_platform(),
        "recommended_python": recommended_python_label(),
        "runtime_python": str(runtime_python) if runtime_python else None,
        "status_counts": status_counts,
        "tools": tools,
    }


def save_audit_report(report: dict, output_path: str | Path) -> Path:
    """Save a JSON audit report to disk."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output


def summarize_audit_report(report: dict) -> list[str]:
    """Return human-readable summary lines for an audit report."""
    tools = report["tools"]
    ready_tools = [tool["id"] for tool in tools if tool["availability"] == "READY"]
    problem_tools = [tool for tool in tools if tool["availability"] not in {"READY", "DOCS ONLY"}]

    lines = [
        f"Generated: {report['generated_at']}",
        f"Platform: {report['platform']}",
        f"Runtime Python: {report['runtime_python'] or 'not found'}",
        f"Recommended Python: {report['recommended_python']}",
        "",
        "Status counts:",
    ]

    for status in sorted(report["status_counts"]):
        lines.append(f"  {status}: {report['status_counts'][status]}")

    lines.extend(
        [
            "",
            f"Ready tools ({len(ready_tools)}): {', '.join(ready_tools) if ready_tools else 'none'}",
            f"Tools needing attention ({len(problem_tools)}):",
        ]
    )

    if not problem_tools:
        lines.append("  none")
        return lines

    for tool in problem_tools:
        lines.append(f"  {tool['id']}: {tool['availability']} - {tool['detail']}")

    return lines
