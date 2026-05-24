#!/usr/bin/env python3
"""
OSINT Hub - Test Suite
Verify all components work correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from osinthub.core.console import configure_console, print_safe

configure_console()

print_safe("=" * 60)
print_safe("OSINT Hub - Component Test")
print_safe("=" * 60)

all_passed = True


def test(description, func):
    global all_passed
    try:
        print_safe(f"\nTesting: {description}...", end=" ")
        func()
        print_safe("PASSED")
        return True
    except Exception as e:
        print_safe(f"FAILED: {e}")
        all_passed = False
        return False


def test_registry():
    from osinthub.tools.registry import ToolRegistry

    registry = ToolRegistry()
    tools = registry.get_all_tools()
    assert len(tools) > 0, "No tools loaded"
    assert any(tool.id == "sherlock" for tool in tools), "Sherlock not found"


def test_tool_manager():
    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    assert tool_manager is not None


def test_results():
    from osinthub.core.results_manager import ResultsManager

    results_manager = ResultsManager()
    assert results_manager is not None


def test_config():
    from osinthub.core.config_manager import ConfigManager

    config_manager = ConfigManager()
    assert config_manager.get("theme") == "dark"


def test_search():
    from osinthub.tools.registry import ToolRegistry

    registry = ToolRegistry()
    results = registry.search_tools("username")
    assert len(results) > 0, "No username tools found"


def test_category():
    from osinthub.tools.registry import ToolCategory, ToolRegistry

    registry = ToolRegistry()
    tools = registry.get_tools_by_category(ToolCategory.USERNAME_SEARCH)
    assert len(tools) > 0, "No username search tools"


def test_cli_argument_parser():
    import cli

    sherlock = cli.registry.get_tool("sherlock")
    harvester = cli.registry.get_tool("harvester")

    sherlock_args = cli.parse_tool_arguments(sherlock, ["--username", "alice", "--print", "true"])
    harvester_args = cli.parse_tool_arguments(harvester, ["-d", "example.com", "-b", "all"])

    assert sherlock_args["username"] == "alice"
    assert sherlock_args["print"] is True
    assert harvester_args["domain"] == "example.com"
    assert harvester_args["source"] == "all"


def test_runtime_helpers():
    from osinthub.core.runtime import recommended_python_label, requirements_file, venv_python

    assert recommended_python_label() == "3.11"
    assert requirements_file().name in {"requirements.txt", "requirements-py311.txt"}
    assert ".venv" in str(venv_python())


def test_git_tools_do_not_false_positive():
    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    reconng = tool_manager.registry.get_tool("reconng")
    assert reconng is not None
    reconng.install_path = ""
    assert tool_manager.check_tool_installed(reconng) is False


def test_tool_audit_report():
    from osinthub.core.tool_audit import build_audit_report
    from osinthub.core.tool_manager import ToolManager

    report = build_audit_report(ToolManager())
    assert "tools" in report and len(report["tools"]) > 0
    assert "status_counts" in report
    assert any(tool["id"] == "sherlock" for tool in report["tools"])


def test_socialscan_dns_failure_detection():
    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    socialscan = tool_manager.registry.get_tool("socialscan")
    assert socialscan is not None

    sample_output = """
----------------------------------------
              danieldepaor
----------------------------------------
GitHub: ClientConnectorDNSError - Cannot connect to host github.com:443 ssl:default [Could not contact DNS servers]
GitLab: ClientConnectorDNSError - Cannot connect to host gitlab.com:443 ssl:default [Could not contact DNS servers]
Instagram: ClientConnectorDNSError - Cannot connect to host www.instagram.com:443 ssl:default [Could not contact DNS servers]
Reddit: ClientConnectorDNSError - Cannot connect to host www.reddit.com:443 ssl:default [Could not contact DNS servers]
Available, Taken/Reserved, Invalid, Error
Completed 8 queries in 0.03s
"""

    success, message = tool_manager._evaluate_tool_output(socialscan, sample_output)
    assert success is False
    assert "dns" in message.lower() or "provider" in message.lower()


def test_exiftool_registry_configuration():
    from osinthub.tools.registry import InstallationMethod, ToolRegistry

    registry = ToolRegistry()
    exiftool = registry.get_tool("exiftool")
    assert exiftool is not None
    assert exiftool.installation_method == InstallationMethod.GIT
    assert exiftool.run_command == "perl exiftool"
    assert "perl" in exiftool.required_commands


def test_windows_safe_git_cleanup():
    import stat
    import tempfile
    from pathlib import Path

    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir = Path(temp_dir) / "git-tool"
        nested_dir = target_dir / ".git" / "objects" / "pack"
        nested_dir.mkdir(parents=True)
        pack_index = nested_dir / "pack-test.idx"
        pack_index.write_text("placeholder", encoding="utf-8")
        pack_index.chmod(stat.S_IREAD)

        tool_manager._remove_tree(target_dir)
        assert not target_dir.exists()


def test_failed_git_install_clears_stale_install_path():
    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    spiderfoot = tool_manager.registry.get_tool("spiderfoot")
    assert spiderfoot is not None

    original_install_git = tool_manager._install_git
    try:
        def fake_install_git(tool, callback):
            return False, "simulated failure"

        tool_manager._install_git = fake_install_git
        spiderfoot.install_path = "stale-path"

        success, _ = tool_manager.install_tool(spiderfoot)
        assert success is False
        assert spiderfoot.install_path == ""
    finally:
        tool_manager._install_git = original_install_git


def test_install_error_summary_for_build_tools():
    import subprocess

    from osinthub.core.tool_manager import ToolManager

    tool_manager = ToolManager()
    error = subprocess.CalledProcessError(
        1,
        ["pip", "install", "lxml"],
        output="error: failed-wheel-build-for-install",
        stderr='error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"',
    )

    summary = tool_manager._format_subprocess_error(error)
    assert "visual c++" in summary.lower()
    assert "build tools" in summary.lower()


test("Tool Registry", test_registry)
test("Tool Manager", test_tool_manager)
test("Results Manager", test_results)
test("Config Manager", test_config)
test("Tool Search", test_search)
test("Category Filter", test_category)
test("CLI Argument Parsing", test_cli_argument_parser)
test("Runtime Helpers", test_runtime_helpers)
test("Git Tool Detection", test_git_tools_do_not_false_positive)
test("Tool Audit Report", test_tool_audit_report)
test("SocialScan DNS Failure Detection", test_socialscan_dns_failure_detection)
test("ExifTool Registry Configuration", test_exiftool_registry_configuration)
test("Windows Safe Git Cleanup", test_windows_safe_git_cleanup)
test("Failed Git Install Cleanup", test_failed_git_install_clears_stale_install_path)
test("Install Error Summary", test_install_error_summary_for_build_tools)

print_safe("\n" + "=" * 60)
if all_passed:
    print_safe("All tests passed!")
    print_safe("OSINT Hub is ready to use.")
else:
    print_safe("Some tests failed")
    print_safe("Check the errors above.")
print_safe("=" * 60)
