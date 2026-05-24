#!/usr/bin/env python3
"""
OSINT Hub - Interactive Menu (Beginner-friendly CLI)
Simple numbered menu system for users not comfortable with complex commands.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from osinthub.core.runtime import maybe_reexec_in_project_venv

if Path(sys.argv[0]).stem.lower() == "menu":
    maybe_reexec_in_project_venv(PROJECT_ROOT)

from osinthub.core.console import configure_console, print_safe
from osinthub.core.results_manager import ResultsManager
from osinthub.core.tool_manager import ToolManager
from osinthub.tools.registry import ToolCategory

configure_console()

tool_manager = ToolManager()
registry = tool_manager.registry
results_manager = ResultsManager()


def print_banner():
    print_safe("\n" + "=" * 60)
    print_safe("OSINT Hub - Interactive Menu")
    print_safe("=" * 60)


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def pause():
    input("\nPress Enter to continue...")


def infer_target(params):
    for key in ("target", "username", "domain", "number", "profile", "query"):
        value = params.get(key)
        if value:
            return str(value)
    return "unknown"


def list_tools():
    """Display all tools with numbers."""
    print_safe("\nAvailable Tools:\n")
    tool_manager.refresh_tool_states(persist=False)
    tools = registry.get_all_tools()

    for index, tool in enumerate(tools, 1):
        status, _ = tool_manager.get_tool_availability(tool)
        print_safe(f"  {index}. [{status}] {tool.icon} {tool.name}")
        print_safe(f"     {tool.description}\n")


def show_categories():
    """Show category menu."""
    print_safe("\nSelect Category:\n")
    categories = list(ToolCategory)
    for index, category in enumerate(categories, 1):
        print_safe(f"  {index}. {category.value}")
    print_safe(f"  {len(categories) + 1}. All Tools")
    print_safe("  0. Back")


def install_tool_interactive():
    """Interactive tool installation."""
    list_tools()
    print_safe("\nEnter tool number to install (or 0 to cancel):")
    try:
        choice = int(input("Choice: "))
        if choice == 0:
            return

        tools = registry.get_all_tools()
        if 1 <= choice <= len(tools):
            tool = tools[choice - 1]
            if tool_manager.check_tool_installed(tool):
                print_safe(f"\n{tool.name} is already installed.")
                if input("Reinstall? (y/N): ").lower() == "y":
                    tool_manager.uninstall_tool(tool)
                else:
                    return

            print_safe(f"\nInstalling {tool.name}...")
            success, message = tool_manager.install_tool(tool)
            if success:
                print_safe(f"{tool.name} installed.")
            else:
                print_safe(f"Failed: {message}")
                print_safe(f"\nManual install: {tool_manager.get_install_guide(tool)}")

            pause()
        else:
            print_safe("Invalid choice.")
    except ValueError:
        print_safe("Please enter a number.")


def run_tool_interactive():
    """Interactive tool runner."""
    print_safe("\nSelect a tool to run:\n")
    installed_tools = [tool for tool in registry.get_all_tools() if tool_manager.check_tool_installed(tool)]

    if not installed_tools:
        print_safe("No runnable tools detected. Install one first.")
        pause()
        return

    for index, tool in enumerate(installed_tools, 1):
        print_safe(f"  {index}. {tool.icon} {tool.name}")
    print_safe("  0. Back")

    try:
        choice = int(input("\nChoice: "))
        if choice == 0:
            return

        if 1 <= choice <= len(installed_tools):
            tool = installed_tools[choice - 1]
            run_tool_with_input(tool)
        else:
            print_safe("Invalid choice.")
    except ValueError:
        print_safe("Please enter a number.")


def run_tool_with_input(tool):
    """Get parameters from user and run tool."""
    print_safe(f"\n{'=' * 60}")
    print_safe(f"Running: {tool.name}")
    print_safe("=" * 60)

    params = {}
    for param in tool.parameters:
        if param.required:
            prompt = f"{param.name} ({param.description}): "
        else:
            prompt = f"{param.name} [{param.default or ''}]: "

        value = input(prompt).strip()

        if value:
            if param.type == "boolean":
                params[param.name] = value.lower() in ("y", "yes", "true", "1")
            else:
                params[param.name] = value
        elif param.default is not None:
            params[param.name] = param.default
        elif param.required:
            print_safe(f"{param.name} is required. Skipping run.")
            pause()
            return

    print_safe(f"\nStarting {tool.name}...")
    success, stdout, stderr = tool_manager.run_tool(tool, params)

    print_safe("=" * 60)
    if success:
        print_safe("Scan completed.\n")
        if stdout:
            print_safe(stdout)

        target = infer_target(params)
        try:
            scan_result = results_manager.save_result(tool, target, stdout)
            print_safe(f"\nResult saved (ID: {scan_result.result_id})")
        except Exception as exc:
            print_safe(f"\nWarning: scan finished but the result could not be saved: {exc}")
    else:
        print_safe("Scan failed.\n")
        if stdout:
            print_safe(stdout)
        if stderr:
            print_safe(stderr)

    pause()


def view_results():
    """View saved results."""
    results = results_manager.get_results(limit=50)
    print_safe(f"\nScan Results ({len(results)} most recent):\n")
    print_safe(f"{'ID':<12} {'Tool':<20} {'Target':<25} {'Time':<19}")
    print_safe("-" * 80)

    for result in results:
        print_safe(
            f"{result.result_id:<12} "
            f"{result.data.get('tool_name', ''):<20} "
            f"{result.target:<25} "
            f"{result.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<19}"
        )

    print_safe("")
    pause()


def export_results():
    """Export results menu."""
    print_safe("\nExport Format:")
    print_safe("  1. JSON")
    print_safe("  2. CSV")
    print_safe("  3. TXT")
    print_safe("  4. HTML")
    print_safe("  0. Cancel")

    try:
        fmt_choice = int(input("\nSelect format: "))
        formats = {1: "json", 2: "csv", 3: "txt", 4: "html"}
        if fmt_choice not in formats:
            return

        fmt = formats[fmt_choice]
        filename = input(f"Output filename [results.{fmt}]: ").strip()
        if not filename:
            filename = f"results.{fmt}"

        results = results_manager.get_results(limit=1000)
        if results_manager.export_results(results, filename, fmt):
            print_safe(f"\nExported {len(results)} results to {filename}")
        else:
            print_safe("Export failed")
    except ValueError:
        print_safe("Invalid choice")
    pause()


def show_tool_info():
    """Show detailed tool information."""
    list_tools()
    print_safe("\nEnter tool number for details (or 0 to cancel):")
    try:
        choice = int(input("Choice: "))
        if choice == 0:
            return

        tools = registry.get_all_tools()
        if 1 <= choice <= len(tools):
            tool = tools[choice - 1]
            print_safe(f"\n{'=' * 60}")
            print_safe(f"{tool.icon} {tool.name}")
            print_safe("=" * 60)
            print_safe(f"Category: {tool.category.value}")
            print_safe(f"\nDescription:\n{tool.long_description or tool.description}\n")
            print_safe(f"Homepage: {tool.homepage or 'N/A'}")
            if tool.examples:
                print_safe("\nExamples:")
                for example in tool.examples:
                    print_safe(f"  $ {example}")
            print_safe(f"\nInstall: {tool.install_command}")
        else:
            print_safe("Invalid choice.")
    except ValueError:
        print_safe("Please enter a number.")
    pause()


def main_menu():
    """Main interactive menu."""
    while True:
        clear_screen()
        print_banner()
        print_safe("\nMain Menu:\n")
        print_safe("  1. Browse & Install Tools")
        print_safe("  2. Run an Installed Tool")
        print_safe("  3. View Results")
        print_safe("  4. Export Results")
        print_safe("  5. Quick Setup (install recommended tools)")
        print_safe("  6. Show Tool Info")
        print_safe("  0. Exit")

        try:
            choice = int(input("\nChoice: "))

            if choice == 1:
                install_tool_interactive()
            elif choice == 2:
                run_tool_interactive()
            elif choice == 3:
                view_results()
            elif choice == 4:
                export_results()
            elif choice == 5:
                quick_setup()
            elif choice == 6:
                show_tool_info()
            elif choice == 0:
                print_safe("\nGoodbye!")
                break
            else:
                print_safe("Invalid choice")
                pause()
        except ValueError:
            print_safe("Please enter a number")
            pause()
        except KeyboardInterrupt:
            print_safe("\n\nGoodbye!")
            break


def quick_setup():
    """Quick setup wizard for beginners."""
    print_safe("\n" + "=" * 60)
    print_safe("Quick Setup - Recommended Starter Pack")
    print_safe("=" * 60)
    print_safe("\nFor beginners, we recommend installing these tools first:\n")
    print_safe("  1. Sherlock - Search usernames across social media")
    print_safe("  2. theHarvester - Find emails and subdomains")
    print_safe("  3. SocialScan - Check username/email availability")
    print_safe("  4. Instaloader - Download Instagram metadata and media")
    print_safe("\nThese tools are the most portable options in the current bundle.")

    response = input("\nInstall all 4? (Y/n): ").lower()
    if response in ("y", "yes", ""):
        recommended = ["sherlock", "harvester", "socialscan", "instaloader"]
        for tool_id in recommended:
            tool = registry.get_tool(tool_id)
            if not tool:
                continue

            print_safe(f"\nInstalling {tool.name}...")
            success, message = tool_manager.install_tool(tool)
            if success:
                print_safe(f"  {tool.name} installed")
            else:
                print_safe(f"  Failed: {message}")

        print_safe("\nSetup complete. You can now run these tools.")
        print_safe("Go to 'Run an Installed Tool' to start.")
    else:
        print_safe("Skipped. You can install tools individually.")

    pause()


def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print_safe("\n\nGoodbye!")
    except Exception as e:
        print_safe(f"\nUnexpected error: {e}")
        print_safe("Please report this bug.")


if __name__ == "__main__":
    main()
