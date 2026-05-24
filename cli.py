#!/usr/bin/env python3
"""
OSINT Hub CLI Interface
Command-line interface for advanced users and scripting.
"""

import argparse
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from osinthub.core.runtime import maybe_reexec_in_project_venv

if Path(sys.argv[0]).stem.lower() in {"cli", "osinthub-cli"}:
    maybe_reexec_in_project_venv(PROJECT_ROOT)

from osinthub.core.console import configure_console, print_safe
from osinthub.core.results_manager import ResultsManager
from osinthub.core.tool_audit import build_audit_report, save_audit_report, summarize_audit_report
from osinthub.core.tool_manager import ToolManager
from osinthub.tools.registry import ToolCategory

configure_console()

tool_manager = ToolManager()
registry = tool_manager.registry
results_manager = ResultsManager()


def parse_tool_arguments(tool, raw_args):
    """Map CLI arguments to the tool parameter names expected by ToolManager."""
    params = {}
    flag_map = {}
    positional_params = []

    for param in tool.parameters:
        if param.flag:
            flag_map[param.flag] = param
        positional_params.append(param) if not param.flag else None

    positional_index = 0
    i = 0
    while i < len(raw_args):
        arg = raw_args[i]

        if arg == "--":
            i += 1
            continue

        if arg.startswith("-"):
            param = flag_map.get(arg)
            if not param:
                normalized_name = arg.lstrip("-").replace("-", "_")
                param = next((p for p in tool.parameters if p.name == normalized_name), None)

            if not param:
                raise ValueError(f"Unknown argument: {arg}")

            if param.type == "boolean":
                if i + 1 < len(raw_args) and not raw_args[i + 1].startswith("-"):
                    next_value = raw_args[i + 1].strip().lower()
                    if next_value in {"true", "false", "1", "0", "yes", "no", "y", "n"}:
                        params[param.name] = next_value in {"true", "1", "yes", "y"}
                        i += 2
                        continue
                params[param.name] = True
                i += 1
                continue

            if i + 1 >= len(raw_args):
                raise ValueError(f"Missing value for {arg}")

            params[param.name] = raw_args[i + 1]
            i += 2
            continue

        if positional_index >= len(positional_params):
            raise ValueError(f"Unexpected positional argument: {arg}")

        params[positional_params[positional_index].name] = arg
        positional_index += 1
        i += 1

    return params


def infer_target(params):
    """Pick the best label for saved results."""
    for key in ("target", "username", "domain", "number", "profile", "query"):
        value = params.get(key)
        if value:
            return str(value)
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="OSINT Hub CLI - All-in-One OSINT Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  osinthub list                    List all available tools
  osinthub list --category "Username Search"
  osinthub search username         Search for tools by keyword
  osinthub info sherlock           Show detailed info about a tool
  osinthub install sherlock        Install a tool
  osinthub run sherlock --username target_user
  osinthub results                 Show all scan results
  osinthub export --format json    Export results
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List tools")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--installed", "-i", action="store_true", help="Show only installed tools")

    search_parser = subparsers.add_parser("search", help="Search tools")
    search_parser.add_argument("query", help="Search query")

    info_parser = subparsers.add_parser("info", help="Show tool info")
    info_parser.add_argument("tool_id", help="Tool ID to inspect")

    install_parser = subparsers.add_parser("install", help="Install a tool")
    install_parser.add_argument("tool_id", help="Tool ID to install")

    run_parser = subparsers.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool_id", help="Tool ID to run")
    run_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the tool, for example: --username target_user",
    )

    subparsers.add_parser("results", help="Show results")

    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument(
        "--format",
        "-f",
        default="json",
        choices=["json", "csv", "txt", "html"],
        help="Export format",
    )
    export_parser.add_argument("--output", "-o", default="osinthub_export.json", help="Output file")

    audit_parser = subparsers.add_parser("audit", help="Audit tool availability and startup health")
    audit_parser.add_argument("--output", "-o", default="tool_audit_latest.json", help="Output JSON file")
    audit_parser.add_argument("--quiet", action="store_true", help="Only save the JSON report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        handle_list(args)
    elif args.command == "search":
        handle_search(args)
    elif args.command == "info":
        handle_info(args)
    elif args.command == "install":
        handle_install(args)
    elif args.command == "run":
        handle_run(args)
    elif args.command == "results":
        handle_results(args)
    elif args.command == "export":
        handle_export(args)
    elif args.command == "audit":
        handle_audit(args)


def handle_list(args):
    """List tools."""
    tools = registry.get_all_tools()
    tool_manager.refresh_tool_states(persist=False)

    if args.category:
        try:
            category = ToolCategory(args.category)
            tools = registry.get_tools_by_category(category)
        except ValueError:
            print_safe(f"Invalid category: {args.category}")
            print_safe(f"Valid categories: {[c.value for c in ToolCategory]}")
            sys.exit(1)

    if args.installed:
        tools = [tool for tool in tools if tool_manager.check_tool_installed(tool)]

    print_safe(f"\n{'ID':<20} {'Name':<25} {'Category':<25} {'Status':<15}")
    print_safe("=" * 90)
    for tool in tools:
        status, _ = tool_manager.get_tool_availability(tool)
        print_safe(f"{tool.id:<20} {tool.name:<25} {tool.category.value:<25} {status:<15}")

    print_safe(f"\nTotal: {len(tools)} tools\n")


def handle_search(args):
    """Search tools."""
    results = registry.search_tools(args.query)

    print_safe(f"\nSearch results for '{args.query}':")
    print_safe("=" * 60)
    for tool in results:
        print_safe(f"{tool.icon} {tool.name}")
        print_safe(f"  {tool.description}")
        print_safe(f"  Category: {tool.category.value}")
        print_safe(f"  ID: {tool.id}")
        print_safe("")


def handle_info(args):
    """Show tool details."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print_safe(f"Tool '{args.tool_id}' not found.")
        print_safe("Use 'osinthub list' to see available tools.")
        sys.exit(1)

    print_safe(f"\n{tool.icon} {tool.name}")
    print_safe("=" * 60)
    print_safe(f"ID: {tool.id}")
    print_safe(f"Category: {tool.category.value}")
    availability, detail = tool_manager.get_tool_availability(tool)
    print_safe(f"Availability: {availability}")
    print_safe(f"Status: {detail}")
    print_safe(f"Description: {tool.long_description or tool.description}")
    print_safe(f"Homepage: {tool.homepage or 'N/A'}")
    print_safe(f"Install: {tool.install_command}")

    if tool.examples:
        print_safe("\nExamples:")
        for example in tool.examples:
            print_safe(f"  $ {example}")

    if tool.parameters:
        print_safe("\nParameters:")
        for param in tool.parameters:
            required = "(required)" if param.required else ""
            flag = param.flag or "<positional>"
            print_safe(f"  {param.name} {flag} {required}".rstrip())
            print_safe(f"    {param.description}")
            if param.options:
                print_safe(f"    Options: {', '.join(param.options)}")


def handle_install(args):
    """Install a tool."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print_safe(f"Tool '{args.tool_id}' not found.")
        sys.exit(1)

    if tool_manager.check_tool_installed(tool):
        print_safe(f"{tool.name} is already installed.")
        response = input("Reinstall? (y/N): ").lower()
        if response != "y":
            sys.exit(0)
        tool_manager.uninstall_tool(tool)

    print_safe(f"Installing {tool.name}...")
    success, message = tool_manager.install_tool(tool)

    if success:
        print_safe(f"{tool.name} installed successfully.")
    else:
        print_safe(f"Installation failed: {message}")
        print_safe("\nManual installation:")
        print_safe(tool_manager.get_install_guide(tool))
        sys.exit(1)


def handle_run(args):
    """Run a tool."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print_safe(f"Tool '{args.tool_id}' not found.")
        sys.exit(1)

    if not tool_manager.check_tool_installed(tool):
        print_safe(f"{tool.name} is not installed.")
        print_safe(f"Install it first: osinthub install {tool.id}")
        sys.exit(1)

    try:
        params = parse_tool_arguments(tool, args.args)
    except ValueError as exc:
        print_safe(f"Argument error: {exc}")
        sys.exit(1)

    print_safe(f"Running {tool.name}...")
    success, stdout, stderr = tool_manager.run_tool(tool, params)

    if success:
        print_safe("Scan completed successfully\n")
        if stdout:
            print_safe(stdout)

        target = infer_target(params)
        try:
            result = results_manager.save_result(tool, target, stdout)
            print_safe(f"\nResult saved (ID: {result.result_id})")
        except Exception as exc:
            print_safe(f"\nWarning: scan finished but the result could not be saved: {exc}")
        return

    print_safe("Scan failed\n")
    if stdout:
        print_safe(stdout)
    if stderr:
        print_safe(stderr)
    sys.exit(1)


def handle_results(args):
    """Show results."""
    results = results_manager.get_results(limit=50)

    print_safe(f"\nScan Results ({len(results)} most recent):")
    print_safe("=" * 85)
    print_safe(f"{'ID':<12} {'Tool':<20} {'Target':<25} {'Time':<20}")
    print_safe("-" * 85)

    for result in results:
        print_safe(
            f"{result.result_id:<12} "
            f"{result.data.get('tool_name', ''):<20} "
            f"{result.target:<25} "
            f"{result.timestamp.strftime('%Y-%m-%d %H:%M'):<20}"
        )

    print_safe("")


def handle_export(args):
    """Export results."""
    results = results_manager.get_results(limit=1000)
    if not results:
        print_safe("No results to export.")
        sys.exit(0)

    success = results_manager.export_results(results, args.output, args.format)
    if success:
        print_safe(f"Exported {len(results)} results to {args.output}")
    else:
        print_safe("Export failed")
        sys.exit(1)


def handle_audit(args):
    """Generate a full tool audit report."""
    report = build_audit_report(tool_manager)
    output_path = save_audit_report(report, args.output)

    if not args.quiet:
        for line in summarize_audit_report(report):
            print_safe(line)
        print_safe("")

    print_safe(f"Saved audit report to {output_path}")


if __name__ == "__main__":
    main()
