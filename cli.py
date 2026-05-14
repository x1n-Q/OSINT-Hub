#!/usr/bin/env python3
"""
OSINT Hub CLI Interface
Command-line interface for advanced users and scripting.
"""

import argparse
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from osinthub.tools.registry import ToolRegistry, ToolCategory
from osinthub.core.tool_manager import ToolManager
from osinthub.core.results_manager import ResultsManager

registry = ToolRegistry()
tool_manager = ToolManager()
results_manager = ResultsManager()

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
  osinthub results                Show all scan results
  osinthub export --format json   Export results
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List tools")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--installed", "-i", action="store_true", help="Show only installed tools")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search tools")
    search_parser.add_argument("query", help="Search query")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show tool info")
    info_parser.add_argument("tool_id", help="Tool ID to inspect")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a tool")
    install_parser.add_argument("tool_id", help="Tool ID to install")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool_id", help="Tool ID to run")
    run_parser.add_argument("args", nargs="*", help="Arguments to pass to tool")

    # Results command
    subparsers.add_parser("results", help="Show results")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument("--format", "-f", default="json", choices=["json", "csv", "txt", "html"],
                               help="Export format")
    export_parser.add_argument("--output", "-o", default="osinthub_export.json", help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to command handlers
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

def handle_list(args):
    """List tools."""
    tools = registry.get_all_tools()

    if args.category:
        try:
            cat = ToolCategory(args.category)
            tools = registry.get_tools_by_category(cat)
        except ValueError:
            print(f"Invalid category: {args.category}")
            print(f"Valid categories: {[c.value for c in ToolCategory]}")
            sys.exit(1)

    if args.installed:
        tools = [t for t in tools if t.installed or tool_manager.check_tool_installed(t)]

    print(f"\n{'ID':<20} {'Name':<25} {'Category':<25} {'Status':<10}")
    print("="*85)
    for tool in tools:
        status = "✓ Installed" if tool.installed or tool_manager.check_tool_installed(tool) else "✗ Not Installed"
        print(f"{tool.id:<20} {tool.name:<25} {tool.category.value:<25} {status:<10}")

    print(f"\nTotal: {len(tools)} tools\n")

def handle_search(args):
    """Search tools."""
    results = registry.search_tools(args.query)

    print(f"\nSearch results for '{args.query}':")
    print("="*60)
    for tool in results:
        print(f"{tool.icon} {tool.name}")
        print(f"  {tool.description}")
        print(f"  Category: {tool.category.value}")
        print(f"  ID: {tool.id}")
        print()

def handle_info(args):
    """Show tool details."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print(f"Tool '{args.tool_id}' not found.")
        print("Use 'osinthub list' to see available tools.")
        sys.exit(1)

    print(f"\n{tool.icon} {tool.name}")
    print("="*60)
    print(f"ID: {tool.id}")
    print(f"Category: {tool.category.value}")
    print(f"Description: {tool.long_description or tool.description}")
    print(f"Homepage: {tool.homepage}")

    if tool.examples:
        print("\nExamples:")
        for ex in tool.examples:
            print(f"  $ {ex}")

    if tool.parameters:
        print("\nParameters:")
        for param in tool.parameters:
            req = "(required)" if param.required else ""
            print(f"  {param.name} {param.flag} {req}")
            print(f"    {param.description}")
            if param.options:
                print(f"    Options: {', '.join(param.options)}")

def handle_install(args):
    """Install a tool."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print(f"Tool '{args.tool_id}' not found.")
        sys.exit(1)

    if tool.installed or tool_manager.check_tool_installed(tool):
        print(f"{tool.name} is already installed.")
        response = input("Reinstall? (y/N): ").lower()
        if response != 'y':
            sys.exit(0)
        tool_manager.uninstall_tool(tool)

    print(f"Installing {tool.name}...")
    success, message = tool_manager.install_tool(tool)

    if success:
        tool.installed = True
        print(f"✓ {tool.name} installed successfully!")
    else:
        print(f"✗ Installation failed: {message}")
        print(f"\nManual installation:")
        print(tool_manager.get_install_guide(tool))
        sys.exit(1)

def handle_run(args):
    """Run a tool."""
    tool = registry.get_tool(args.tool_id)
    if not tool:
        print(f"Tool '{args.tool_id}' not found.")
        sys.exit(1)

    if not tool.installed and not tool_manager.check_tool_installed(tool):
        print(f"{tool.name} is not installed.")
        print(f"Install it first: osinthub install {tool.id}")
        sys.exit(1)

    # Parse arguments from CLI
    params = {}
    i = 0
    while i < len(args.args):
        arg = args.args[i]
        if arg.startswith("-"):
            if i + 1 < len(args.args) and not args.args[i+1].startswith("-"):
                params[arg.lstrip("-")] = args.args[i+1]
                i += 2
            else:
                params[arg.lstrip("-")] = True
                i += 1
        else:
            # Positional argument - first one might be target
            if not params:
                params["target"] = arg
            i += 1

    print(f"Running {tool.name}...")
    success, stdout, stderr = tool_manager.run_tool(tool, params)

    if success:
        print("✓ Scan completed successfully\n")
        print(stdout)

        # Save result
        target = params.get("target", params.get("username", params.get("domain", "unknown")))
        result = results_manager.save_result(tool, target, stdout)
        print(f"\nResult saved (ID: {result.result_id})")
    else:
        print("✗ Scan failed\n")
        print(stdout)
        print(stderr)
        sys.exit(1)

def handle_results(args):
    """Show results."""
    results = results_manager.get_results(limit=50)

    print(f"\nScan Results ({len(results)} most recent):")
    print("="*85)
    print(f"{'ID':<12} {'Tool':<20} {'Target':<25} {'Time':<20}")
    print("-"*85)

    for result in results:
        print(f"{result.result_id:<12} {result.data.get('tool_name',''):<20} {result.target:<25} {result.timestamp.strftime('%Y-%m-%d %H:%M'):<20}")

    print()

def handle_export(args):
    """Export results."""
    results = results_manager.get_results(limit=1000)
    if not results:
        print("No results to export.")
        sys.exit(0)

    success = results_manager.export_results(results, args.output, args.format)
    if success:
        print(f"✓ Exported {len(results)} results to {args.output}")
    else:
        print("✗ Export failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
