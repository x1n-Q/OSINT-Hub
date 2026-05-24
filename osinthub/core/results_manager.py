"""
Results Manager
Handles tool output storage, parsing, and export functionality.
"""

import json
import csv
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

from osinthub.core.paths import get_osinthub_home
from osinthub.tools.registry import ToolCategory, OSINTTool

class ScanResult:
    """Represents a single scan result."""
    def __init__(self, tool_id: str, target: str, data: Any, timestamp: datetime = None):
        self.tool_id = tool_id
        self.target = target
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.result_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID for this result."""
        content = f"{self.tool_id}_{self.target}_{self.timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict:
        return {
            "result_id": self.result_id,
            "tool_id": self.tool_id,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanResult':
        result = cls(
            tool_id=data["tool_id"],
            target=data["target"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        result.result_id = data["result_id"]
        return result

class ResultsManager:
    """Manages storing, retrieving, and exporting scan results."""

    def __init__(self, results_dir: str = None):
        self.results_dir = Path(results_dir or get_osinthub_home() / "results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self._results: Dict[str, ScanResult] = {}
        self._load_index()

    def _load_index(self):
        """Load existing results index."""
        index_file = self.results_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for result_data in data:
                    result = ScanResult.from_dict(result_data)
                    self._results[result.result_id] = result
            except Exception as e:
                print(f"Error loading results index: {e}")

    def _save_index(self):
        """Save results index to disk."""
        index_file = self.results_dir / "index.json"
        data = [r.to_dict() for r in self._results.values()]
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def save_result(self, tool: OSINTTool, target: str, raw_output: str,
                    parsed_data: Optional[Dict] = None) -> ScanResult:
        """
        Save a tool scan result.

        Args:
            tool: The tool that was run
            target: What was scanned
            raw_output: Raw stdout from the tool
            parsed_data: Optional parsed/dict representation

        Returns:
            ScanResult object
        """
        result = ScanResult(
            tool_id=tool.id,
            target=target,
            data={
                "raw": raw_output,
                "parsed": parsed_data or {},
                "tool_name": tool.name,
                "tool_category": tool.category.value
            }
        )

        # Save individual result file
        result_file = self.results_dir / f"{result.result_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)

        self._results[result.result_id] = result
        self._save_index()

        return result

    def get_results(self, tool_id: str = None, target: str = None,
                    category: ToolCategory = None, limit: int = 100) -> List[ScanResult]:
        """
        Retrieve results with optional filtering.

        Args:
            tool_id: Filter by tool ID
            target: Filter by target string
            category: Filter by tool category
            limit: Maximum number of results to return

        Returns:
            List of matching ScanResult objects
        """
        results = list(self._results.values())

        if tool_id:
            results = [r for r in results if r.tool_id == tool_id]

        if target:
            results = [r for r in results if target.lower() in r.target.lower()]

        if category:
            results = [r for r in results if r.data.get("tool_category") == category.value]

        # Sort by timestamp descending
        results.sort(key=lambda r: r.timestamp, reverse=True)

        return results[:limit]

    def get_result(self, result_id: str) -> Optional[ScanResult]:
        """Get a specific result by ID."""
        return self._results.get(result_id)

    def delete_result(self, result_id: str) -> bool:
        """Delete a result."""
        if result_id in self._results:
            del self._results[result_id]
            result_file = self.results_dir / f"{result_id}.json"
            if result_file.exists():
                result_file.unlink()
            self._save_index()
            return True
        return False

    def clear_results(self):
        """Clear all results."""
        self._results.clear()
        self._save_index()
        for f in self.results_dir.glob("*.json"):
            f.unlink()

    def export_results(self, results: List[ScanResult], filepath: str,
                      format: str = "json") -> bool:
        """
        Export results to file.

        Args:
            results: List of results to export
            filepath: Output file path
            format: Export format (json, csv, txt, html)

        Returns:
            True if successful
        """
        try:
            if format.lower() == "json":
                self._export_json(results, filepath)
            elif format.lower() == "csv":
                self._export_csv(results, filepath)
            elif format.lower() == "txt":
                self._export_txt(results, filepath)
            elif format.lower() == "html":
                self._export_html(results, filepath)
            else:
                return False
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def _export_json(self, results: List[ScanResult], filepath: str):
        """Export to JSON."""
        data = [r.to_dict() for r in results]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _export_csv(self, results: List[ScanResult], filepath: str):
        """Export to CSV."""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tool", "Target", "Timestamp", "Result ID"])

            for result in results:
                writer.writerow([
                    result.data.get("tool_name", result.tool_id),
                    result.target,
                    result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    result.result_id
                ])

    def _export_txt(self, results: List[ScanResult], filepath: str):
        """Export to human-readable text."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"{'='*60}\n")
                f.write(f"Tool: {result.data.get('tool_name', result.tool_id)}\n")
                f.write(f"Target: {result.target}\n")
                f.write(f"Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Result ID: {result.result_id}\n")
                f.write(f"\nRaw Output:\n{'-'*40}\n")
                f.write(result.data.get("raw", "") + "\n")
                f.write(f"\n")

    def _export_html(self, results: List[ScanResult], filepath: str):
        """Export to HTML report."""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OSINT Hub Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .result {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tool-name {{ color: #2c3e50; font-weight: bold; }}
        .target {{ color: #e74c3c; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
        .raw {{ background: #ecf0f1; padding: 15px; border-radius: 4px; white-space: pre-wrap; font-family: monospace; }}
        h2 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OSINT Hub Scan Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total results: {len(results)}</p>
    </div>
"""

        for result in results:
            tool_name = html.escape(str(result.data.get("tool_name", result.tool_id)))
            target = html.escape(str(result.target))
            raw_output = html.escape(str(result.data.get("raw", "")))
            html_content += f"""
    <div class="result">
        <h2>{tool_name}</h2>
        <p class="tool-name">Tool: {tool_name}</p>
        <p class="target">Target: {target}</p>
        <p class="timestamp">Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <h3>Raw Output:</h3>
        <div class="raw">{raw_output}</div>
    </div>
"""
        html_content += """
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def get_statistics(self) -> Dict:
        """Get statistics about stored results."""
        tools_used = set()
        targets = set()
        categories = {}

        for result in self._results.values():
            tools_used.add(result.tool_id)
            targets.add(result.target)
            cat = result.data.get("tool_category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_results": len(self._results),
            "tools_used": len(tools_used),
            "unique_targets": len(targets),
            "categories": categories,
            "latest_scan": max((r.timestamp for r in self._results.values()), default=None).isoformat() if self._results else None
        }
