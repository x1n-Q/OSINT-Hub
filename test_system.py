#!/usr/bin/env python3
"""
OSINT Hub - Test Suite
Verify all components work correctly.
"""

import sys
from pathlib import Path

print("="*60)
print("OSINT Hub - Component Test")
print("="*60)

all_passed = True

def test(description, func):
    global all_passed
    try:
        print(f"\nTesting: {description}...", end=" ")
        func()
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        all_passed = False
        return False

# Test 1: Import registry
def test_registry():
    from osinthub.tools.registry import ToolRegistry
    r = ToolRegistry()
    tools = r.get_all_tools()
    assert len(tools) > 0, "No tools loaded"
    assert any(t.id == "sherlock" for t in tools), "Sherlock not found"

test("Tool Registry", test_registry)

# Test 2: Import tool manager
def test_tool_manager():
    from osinthub.core.tool_manager import ToolManager
    tm = ToolManager()
    assert tm is not None

test("Tool Manager", test_tool_manager)

# Test 3: Import results manager
def test_results():
    from osinthub.core.results_manager import ResultsManager, ScanResult
    rm = ResultsManager()
    assert rm is not None

test("Results Manager", test_results)

# Test 4: Import config manager
def test_config():
    from osinthub.core.config_manager import ConfigManager
    cm = ConfigManager()
    assert cm.get("theme") == "dark"

test("Config Manager", test_config)

# Test 5: Tool search
def test_search():
    from osinthub.tools.registry import ToolRegistry
    r = ToolRegistry()
    results = r.search_tools("username")
    assert len(results) > 0, "No username tools found"

test("Tool Search", test_search)

# Test 6: Category filtering
def test_category():
    from osinthub.tools.registry import ToolRegistry, ToolCategory
    r = ToolRegistry()
    tools = r.get_tools_by_category(ToolCategory.USERNAME_SEARCH)
    assert len(tools) > 0, "No username search tools"

test("Category Filter", test_category)

print("\n" + "="*60)
if all_passed:
    print("✓ All tests passed!")
    print("OSINT Hub is ready to use.")
else:
    print("✗ Some tests failed")
    print("Check the errors above.")
print("="*60)
