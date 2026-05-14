#!/usr/bin/env python3
"""
OSINT Hub - Interactive Menu (Beginner-friendly CLI)
Simple numbered menu system for users not comfortable with complex commands.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from osinthub.tools.registry import ToolRegistry, ToolCategory
from osinthub.core.tool_manager import ToolManager
from osinthub.core.results_manager import ResultsManager

registry = ToolRegistry()
tool_manager = ToolManager()
results_manager = ResultsManager()

def print_banner():
    print("\n" + "="*60)
    print("🔍 OSINT Hub - Interactive Menu")
    print("="*60)

def clear_screen():
    import os
    os.system('clear' if os.name == 'posix' else 'cls')

def pause():
    input("\nPress Enter to continue...")

def list_tools():
    """Display all tools with numbers."""
    print("\nAvailable Tools:\n")
    tools = registry.get_all_tools()
    for i, tool in enumerate(tools, 1):
        status = "✓" if tool.installed or tool_manager.check_tool_installed(tool) else "✗"
        print(f"  {i}. {status} {tool.icon} {tool.name}")
        print(f"     {tool.description}\n")

def show_categories():
    """Show category menu."""
    print("\nSelect Category:\n")
    categories = list(ToolCategory)
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat.value}")
    print(f"  {len(categories)+1}. All Tools")
    print(f"  0. Back")

def install_tool_interactive():
    """Interactive tool installation."""
    list_tools()
    print("\nEnter tool number to install (or 0 to cancel):")
    try:
        choice = int(input("Choice: "))
        if choice == 0:
            return

        tools = registry.get_all_tools()
        if 1 <= choice <= len(tools):
            tool = tools[choice-1]
            if tool.installed or tool_manager.check_tool_installed(tool):
                print(f"\n{tool.name} is already installed.")
                if input("Reinstall? (y/N): ").lower() == 'y':
                    tool_manager.uninstall_tool(tool)
                else:
                    return

            print(f"\nInstalling {tool.name}...")
            import threading
            def do_install():
                success, msg = tool_manager.install_tool(tool)
                if success:
                    print(f"✓ {tool.name} installed!")
                else:
                    print(f"✗ Failed: {msg}")
                    print(f"\nManual install: {tool.install_command}")

            thread = threading.Thread(target=do_install, daemon=True)
            thread.start()
            thread.join(timeout=300)  # 5 minute timeout

            pause()
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")

def run_tool_interactive():
    """Interactive tool runner."""
    print("\nSelect a tool to run:\n")
    installed_tools = [t for t in registry.get_all_tools()
                      if t.installed or tool_manager.check_tool_installed(t)]

    if not installed_tools:
        print("No tools installed. Install some first!")
        pause()
        return

    for i, tool in enumerate(installed_tools, 1):
        print(f"  {i}. {tool.icon} {tool.name}")
    print("  0. Back")

    try:
        choice = int(input("\nChoice: "))
        if choice == 0:
            return

        if 1 <= choice <= len(installed_tools):
            tool = installed_tools[choice-1]
            run_tool_with_input(tool)
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")

def run_tool_with_input(tool):
    """Get parameters from user and run tool."""
    print(f"\n{'='*60}")
    print(f"Running: {tool.name}")
    print('='*60)

    params = {}
    for param in tool.parameters:
        if param.required:
            prompt = f"{param.name} ({param.description}): "
        else:
            prompt = f"{param.name} [{param.default or ''}]: "

        value = input(prompt).strip()

        if value:
            if param.type == "boolean":
                params[param.name] = value.lower() in ('y', 'yes', 'true', '1')
            else:
                params[param.name] = value
        elif param.default:
            params[param.name] = param.default
        elif param.required:
            print(f"  {param.name} is required! Skipping...")
            return

    print(f"\nStarting {tool.name}...")
    import subprocess

    try:
        # Build command
        cmd = [tool.run_command]
        for param in tool.parameters:
            if param.name in params:
                if param.type == "boolean":
                    if params[param.name]:
                        cmd.append(param.flag)
                else:
                    cmd.append(param.flag)
                    cmd.append(str(params[param.name]))

        print(f"Command: {' '.join(cmd)}\n")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=tool.install_path if tool.install_path else None
        )

        print("="*60)
        if result.returncode == 0:
            print("✓ Scan completed!\n")
            print(result.stdout)

            # Save result
            target = params.get("target", params.get("username", params.get("domain", "unknown")))
            scan_result = results_manager.save_result(tool, target, result.stdout)
            print(f"\n📁 Result saved (ID: {scan_result.result_id})")
        else:
            print("✗ Scan failed\n")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("✗ Scan timed out (5 minutes)")
    except Exception as e:
        print(f"✗ Error: {e}")

    pause()

def view_results():
    """View saved results."""
    results = results_manager.get_results(limit=50)
    print(f"\n📊 Scan Results ({len(results)} most recent):\n")
    print(f"{'ID':<12} {'Tool':<20} {'Target':<25} {'Time':<19}")
    print("-"*80)

    for result in results:
        print(f"{result.result_id:<12} {result.data.get('tool_name',''):<20} {result.target:<25} {result.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<19}")

    print()
    pause()

def export_results():
    """Export results menu."""
    print("\nExport Format:")
    print("  1. JSON")
    print("  2. CSV")
    print("  3. TXT")
    print("  4. HTML")
    print("  0. Cancel")

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
            print(f"\n✓ Exported {len(results)} results to {filename}")
        else:
            print("✗ Export failed")
    except ValueError:
        print("Invalid choice")
    pause()

def show_tool_info():
    """Show detailed tool information."""
    list_tools()
    print("\nEnter tool number for details (or 0 to cancel):")
    try:
        choice = int(input("Choice: "))
        if choice == 0:
            return

        tools = registry.get_all_tools()
        if 1 <= choice <= len(tools):
            tool = tools[choice-1]
            print(f"\n{'='*60}")
            print(f"{tool.icon} {tool.name}")
            print('='*60)
            print(f"Category: {tool.category.value}")
            print(f"\nDescription:\n{tool.long_description or tool.description}\n")
            print(f"Homepage: {tool.homepage}")
            if tool.examples:
                print("\nExamples:")
                for ex in tool.examples:
                    print(f"  $ {ex}")
            print(f"\nInstall: {tool.install_command}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")
    pause()

def main_menu():
    """Main interactive menu."""
    while True:
        clear_screen()
        print_banner()
        print("\nMain Menu:\n")
        print("  1. Browse & Install Tools")
        print("  2. Run an Installed Tool")
        print("  3. View Results")
        print("  4. Export Results")
        print("  5. Quick Setup (install recommended tools)")
        print("  6. Show Tool Info")
        print("  0. Exit")

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
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice")
                pause()
        except ValueError:
            print("Please enter a number")
            pause()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

def quick_setup():
    """Quick setup wizard for beginners."""
    print("\n" + "="*60)
    print("🚀 Quick Setup - Recommended Starter Pack")
    print("="*60)
    print("\nFor beginners, we recommend installing these tools first:\n")
    print("  1. Sherlock - Search usernames across social media")
    print("  2. theHarvester - Find emails and subdomains")
    print("  3. ExifTool - Extract metadata from images")
    print("  4. SocialScan - Check username/email availability")
    print("\nThese tools cover the most common OSINT needs.")

    response = input("\nInstall all 4? (Y/n): ").lower()
    if response in ('y', 'yes', ''):
        recommended = ["sherlock", "harvester", "exiftool", "socialscan"]
        for tool_id in recommended:
            tool = registry.get_tool(tool_id)
            if tool:
                print(f"\nInstalling {tool.name}...")
                success, msg = tool_manager.install_tool(tool)
                if success:
                    print(f"  ✓ {tool.name} installed")
                else:
                    print(f"  ✗ Failed: {msg}")

        print("\n✅ Setup complete! You can now run these tools.")
        print("   Go to 'Run an Installed Tool' to start.")
    else:
        print("Skipped. You can install tools individually.")

    pause()

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please report this bug.")

if __name__ == "__main__":
    main()
