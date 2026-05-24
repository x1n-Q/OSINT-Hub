"""
Configuration Manager
Handles user settings, preferences, and configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from osinthub.core.paths import get_osinthub_home

class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or get_osinthub_home() / "config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"

        self._config = self._load_defaults()
        self._load()

    def _load_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "theme": "dark",
            "accent_color": "blue",
            "auto_check_updates": True,
            "save_results": True,
            "results_limit": 1000,
            "default_export_format": "json",
            "output_directory": str((Path(os.environ.get("USERPROFILE", str(Path.home()))) / "osinthub_output")),
            "proxy": None,
            "user_agent": "OSINTHub/1.0",
            "timeout": 30,
            "max_threads": 3,
            "show_notifications": True,
            "confirm_exit": True,
        }

    def _load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                self._config.update(saved)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
        self.save()

    def reset(self):
        """Reset to defaults."""
        self._config = self._load_defaults()
        self.save()

    def as_dict(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config.copy()
