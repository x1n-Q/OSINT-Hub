#!/usr/bin/env python3
"""
Build Windows release artifacts for OSINT Hub with PyInstaller.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from osinthub import __version__
from osinthub.core.console import configure_console, print_safe
from osinthub.core.runtime import recommended_python_label, using_recommended_python

configure_console()

GUI_NAME = "OSINT Hub"
RUNTIME_SETUP_NAME = "OSINT Hub Runtime Setup"
RELEASE_DIR_NAME = "OSINT-Hub-Windows"


def data_arg(source: Path, target: str = ".") -> str:
    return f"{source}{os.pathsep}{target}"


def optional_icon(project_root: Path) -> list[str]:
    for candidate in (
        project_root / "assets" / "osinthub.ico",
        project_root / "assets" / "icon.ico",
        project_root / "icon.ico",
    ):
        if candidate.exists():
            return ["--icon", str(candidate)]
    return []


def run_pyinstaller(arguments: list[str]) -> None:
    try:
        from PyInstaller.__main__ import run as pyinstaller_run
    except ImportError as exc:
        raise RuntimeError(
            "PyInstaller is not installed. Run: python -m pip install -r requirements-build.txt"
        ) from exc

    print_safe(f"$ pyinstaller {' '.join(arguments)}")
    pyinstaller_run(arguments)


def build_gui(project_root: Path, dist_root: Path, work_root: Path, clean: bool) -> Path:
    arguments = [
        str(project_root / "main.py"),
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name",
        GUI_NAME,
        "--distpath",
        str(dist_root),
        "--workpath",
        str(work_root / "gui"),
        "--specpath",
        str(work_root / "spec"),
        "--paths",
        str(project_root),
        "--collect-data",
        "customtkinter",
        "--collect-data",
        "ttkthemes",
        "--collect-submodules",
        "ttkthemes",
        "--hidden-import",
        "PIL._tkinter_finder",
        "--add-data",
        data_arg(project_root / "README.md"),
        "--add-data",
        data_arg(project_root / "LICENSE"),
    ]
    if clean:
        arguments.append("--clean")
    arguments.extend(optional_icon(project_root))
    run_pyinstaller(arguments)
    return dist_root / GUI_NAME


def build_runtime_setup(project_root: Path, dist_root: Path, work_root: Path, clean: bool) -> Path:
    arguments = [
        str(project_root / "bootstrap_runtime.py"),
        "--noconfirm",
        "--onefile",
        "--console",
        "--name",
        RUNTIME_SETUP_NAME,
        "--distpath",
        str(dist_root),
        "--workpath",
        str(work_root / "runtime"),
        "--specpath",
        str(work_root / "spec"),
        "--paths",
        str(project_root),
        "--add-data",
        data_arg(project_root / "LICENSE"),
    ]
    if clean:
        arguments.append("--clean")
    arguments.extend(optional_icon(project_root))
    run_pyinstaller(arguments)
    return dist_root / f"{RUNTIME_SETUP_NAME}.exe"


def write_release_notes(release_dir: Path) -> None:
    notes = "\n".join(
        [
            "OSINT Hub Windows Release",
            "==========================",
            "",
            "1. Start the app with OSINT Hub.exe.",
            "2. Before installing Python-based tools, run OSINT Hub Runtime Setup.exe once.",
            "3. The runtime setup helper looks for Python 3.11 and creates the managed tool runtime.",
            "4. After runtime setup, install and run tools from inside OSINT Hub normally.",
            "",
            "If Python 3.11 is not installed yet, install it first and rerun OSINT Hub Runtime Setup.exe.",
        ]
    )
    (release_dir / "HOW_TO_START.txt").write_text(notes, encoding="utf-8")


def assemble_release(gui_dir: Path, runtime_setup_exe: Path, release_dir: Path, zip_release: bool) -> Path:
    if release_dir.exists():
        shutil.rmtree(release_dir)

    shutil.copytree(gui_dir, release_dir)
    shutil.copy2(runtime_setup_exe, release_dir / runtime_setup_exe.name)
    write_release_notes(release_dir)

    if zip_release:
        archive_base = release_dir.parent / RELEASE_DIR_NAME
        zip_path = shutil.make_archive(str(archive_base), "zip", root_dir=release_dir.parent, base_dir=release_dir.name)
        print_safe(f"Created zip archive: {zip_path}")

    return release_dir


def build(clean: bool = True, zip_release: bool = False) -> Path:
    if os.name != "nt":
        raise RuntimeError("build_exe.py is intended for Windows release builds.")

    if not using_recommended_python():
        print_safe(
            f"WARN Building with Python {sys.version_info.major}.{sys.version_info.minor}. "
            f"Python {recommended_python_label()} is recommended for the most reliable release build."
        )

    project_root = Path(__file__).resolve().parent
    dist_root = project_root / "dist"
    work_root = project_root / "build" / "pyinstaller"
    release_dir = dist_root / RELEASE_DIR_NAME

    gui_dir = build_gui(project_root, dist_root, work_root, clean=clean)
    runtime_setup_exe = build_runtime_setup(project_root, dist_root, work_root, clean=clean)
    assembled = assemble_release(gui_dir, runtime_setup_exe, release_dir, zip_release=zip_release)

    print_safe("")
    print_safe(f"OSINT Hub {__version__} release build complete.")
    print_safe(f"Release folder: {assembled}")
    print_safe(f"Main app: {assembled / (GUI_NAME + '.exe')}")
    print_safe(f"Runtime helper: {assembled / runtime_setup_exe.name}")
    return assembled


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OSINT Hub Windows release bundle.")
    parser.add_argument("--no-clean", action="store_true", help="Reuse existing PyInstaller build state.")
    parser.add_argument("--zip", action="store_true", help="Create a zip archive of the finished release folder.")
    args = parser.parse_args()

    build(clean=not args.no_clean, zip_release=args.zip)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_safe("\nBuild cancelled.")
        raise SystemExit(1)
    except Exception as exc:
        print_safe(f"\nBuild failed: {exc}")
        raise SystemExit(1)
