"""
Path helpers for OSINT Hub data directories.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def _can_write_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:
        return False


def _fallback_home() -> Path:
    cwd_home = Path.cwd() / ".osinthub-local"
    if _can_write_directory(cwd_home):
        return cwd_home

    temp_home = Path(tempfile.gettempdir()) / "osinthub"
    if _can_write_directory(temp_home):
        return temp_home

    return cwd_home


def get_osinthub_home() -> Path:
    """Return the preferred writable OSINT Hub data directory."""
    override = os.environ.get("OSINTHUB_HOME")
    if override:
        return Path(override).expanduser()

    legacy_home = Path.home() / ".osinthub"

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            modern_home = Path(local_app_data) / "OSINT-Hub"
            if modern_home.exists() and _can_write_directory(modern_home):
                return modern_home

            if legacy_home.exists():
                if _can_write_directory(legacy_home):
                    return legacy_home

                if _can_write_directory(modern_home):
                    try:
                        shutil.copytree(legacy_home, modern_home, dirs_exist_ok=True)
                    except Exception:
                        pass
                    return modern_home

            if _can_write_directory(modern_home):
                return modern_home

            fallback_home = _fallback_home()
            if legacy_home.exists():
                try:
                    shutil.copytree(legacy_home, fallback_home, dirs_exist_ok=True)
                except Exception:
                    pass
            return fallback_home

    if legacy_home.exists() and _can_write_directory(legacy_home):
        return legacy_home

    if _can_write_directory(legacy_home):
        return legacy_home

    fallback_home = _fallback_home()
    if legacy_home.exists():
        try:
            shutil.copytree(legacy_home, fallback_home, dirs_exist_ok=True)
        except Exception:
            pass
    return fallback_home
