"""
Tool Installation Manager
Handles installation, updates, and dependency management for OSINT tools.
"""

import importlib.util
import json
import os
import shlex
import shutil
import site
import stat
import subprocess
import sys
import sysconfig
import time
from pathlib import Path
from typing import Callable, Optional, Tuple

from osinthub.core.paths import get_osinthub_home
from osinthub.core.runtime import (
    python_is_virtualenv,
    probe_python,
    recommended_python_label,
    resolve_runtime_python,
    runtime_scripts_dir,
)
from osinthub.tools.registry import InstallationMethod, OSINTTool, ToolRegistry


class ToolManager:
    """Manages installation and execution of OSINT tools."""

    def __init__(self, tools_dir: str = None, config_dir: str = None):
        base_dir = get_osinthub_home()
        self.tools_dir = Path(tools_dir or base_dir / "tools")
        self.config_dir = Path(config_dir or base_dir / "config")
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._healthcheck_cache: dict[str, tuple[bool, str]] = {}
        self._runtime_version: Optional[tuple[int, int, int]] = None

        self.registry = ToolRegistry()
        self._load_installed_state()
        self.refresh_tool_states(persist=False)

    def _resolve_tool(self, tool: OSINTTool) -> OSINTTool:
        return self.registry.get_tool(tool.id) or tool

    def _copy_runtime_state(self, source: OSINTTool, target: OSINTTool) -> None:
        if source is target:
            return
        target.installed = source.installed
        target.install_path = source.install_path

    def _load_installed_state(self):
        """Load which tools are installed from config."""
        state_file = self.config_dir / "installed.json"
        if not state_file.exists():
            return

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                installed = json.load(f)
        except Exception:
            return

        for tool_id, path in installed.items():
            tool = self.registry.get_tool(tool_id)
            if not tool:
                continue
            tool.install_path = path or ""
            tool.installed = bool(path)

    def _save_installed_state(self):
        """Save installed state to config."""
        state_file = self.config_dir / "installed.json"
        installed = {}
        for tool in self.registry.get_all_tools():
            if tool.installed:
                installed[tool.id] = tool.install_path or ""

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(installed, f, indent=2)

    def refresh_tool_states(self, persist: bool = True) -> None:
        """Sync cached tool state with the real environment."""
        changed = False

        for tool in self.registry.get_all_tools():
            if tool.installation_method == InstallationMethod.GIT and tool.install_path:
                if not Path(tool.install_path).exists():
                    tool.install_path = ""
                    self._invalidate_tool_cache(tool.id)

            installed_now = self.check_tool_installed(tool)
            if tool.installed != installed_now:
                tool.installed = installed_now
                changed = True

        if persist and changed:
            self._save_installed_state()

    def _command_parts(self, command: str) -> list:
        if not command:
            return []
        return shlex.split(command, posix=os.name != "nt")

    def _invalidate_tool_cache(self, tool_id: str) -> None:
        self._healthcheck_cache.pop(tool_id, None)

    def _handle_remove_readonly(self, func, path, exc_info) -> None:
        """Retry removal after clearing a Windows read-only attribute."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            raise exc_info[1]

    def _remove_tree(self, target_dir: Path) -> None:
        """Remove a managed tool directory with Windows-safe retries."""
        if not target_dir.exists():
            return

        last_error: Optional[Exception] = None
        for _ in range(3):
            try:
                shutil.rmtree(target_dir, onerror=self._handle_remove_readonly)
                return
            except FileNotFoundError:
                return
            except PermissionError as exc:
                last_error = exc
                time.sleep(0.2)

        raise RuntimeError(
            f"Could not remove the previous installation at {target_dir}. "
            "Close File Explorer, terminals, SpiderFoot, or antivirus tools that may be using this folder, then try again."
        ) from last_error

    def _format_subprocess_error(self, error: subprocess.CalledProcessError, tail_lines: int = 8) -> str:
        """Return a concise, user-facing error summary for failed installs."""
        combined = "\n".join(
            part.strip() for part in (error.stderr, error.stdout) if part and part.strip()
        )
        if not combined:
            return "Unknown error"

        if "Microsoft Visual C++ 14.0 or greater is required" in combined:
            return (
                "A native dependency could not be built because Microsoft Visual C++ 14.0 or greater is required. "
                "Install the Microsoft C++ Build Tools, then retry."
            )

        lines = [line.rstrip() for line in combined.splitlines() if line.strip()]
        if len(lines) <= tail_lines:
            return "\n".join(lines)
        return "\n".join(lines[-tail_lines:])

    def get_runtime_python(self) -> Optional[Path]:
        """Return the preferred Python interpreter for tool installs and python-based tools."""
        return resolve_runtime_python()

    def get_runtime_python_version(self) -> Optional[tuple[int, int, int]]:
        """Return the version of the runtime Python interpreter."""
        if self._runtime_version is not None:
            return self._runtime_version

        runtime_python = self.get_runtime_python()
        if not runtime_python:
            return None

        probe = probe_python([str(runtime_python)])
        if not probe:
            return None

        self._runtime_version = probe[0]
        return self._runtime_version

    def needs_python_runtime(self, tool: OSINTTool) -> bool:
        managed_tool = self._resolve_tool(tool)
        if managed_tool.installation_method == InstallationMethod.PIP:
            return True

        cmd = self._command_parts(managed_tool.run_command)
        return bool(cmd and cmd[0] in {"python", "python3"})

    def get_missing_required_commands(self, tool: OSINTTool) -> list[str]:
        """Return required external commands that are missing for a tool."""
        managed_tool = self._resolve_tool(tool)
        missing = []
        for command in getattr(managed_tool, "required_commands", []):
            if not self._which(command):
                missing.append(command)
        return missing

    def _require_runtime_python(self) -> Path:
        runtime_python = self.get_runtime_python()
        if runtime_python:
            return runtime_python

        raise RuntimeError(
            f"Python {recommended_python_label()} runtime not found. Run bootstrap_runtime.py "
            "or the OSINT Hub Runtime Setup release helper first."
        )

    def _script_search_paths(self) -> list[str]:
        candidates = []

        runtime_dir = runtime_scripts_dir()
        if runtime_dir:
            candidates.append(str(runtime_dir))

        try:
            candidates.append(str(Path(sys.executable).resolve().parent))
        except Exception:
            pass

        try:
            user_base = Path(site.getuserbase())
            candidates.append(str(user_base / ("Scripts" if os.name == "nt" else "bin")))
        except Exception:
            pass

        for scheme in (None, "nt_user", "posix_user"):
            try:
                script_path = sysconfig.get_path("scripts", scheme=scheme) if scheme else sysconfig.get_path("scripts")
            except Exception:
                script_path = None
            if script_path:
                candidates.append(str(Path(script_path)))

        unique = []
        for candidate in candidates:
            if candidate and candidate not in unique:
                unique.append(candidate)

        return unique

    def _build_runtime_env(self, tool: Optional[OSINTTool] = None) -> dict:
        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"

        runtime_python = self.get_runtime_python()
        if runtime_python:
            env["OSINTHUB_RUNTIME_PYTHON"] = str(runtime_python)

        path_entries = self._script_search_paths()
        current_path = env.get("PATH", "")
        if current_path:
            path_entries.append(current_path)
        env["PATH"] = os.pathsep.join(path_entries)

        if tool and tool.install_path and Path(tool.install_path).exists():
            repo_path = str(Path(tool.install_path))
            existing_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = repo_path if not existing_pythonpath else repo_path + os.pathsep + existing_pythonpath

        return env

    def _which(self, command: str, env: Optional[dict] = None) -> Optional[str]:
        runtime_env = env or self._build_runtime_env()
        return shutil.which(command, path=runtime_env.get("PATH"))

    def _resolve_command_reference(self, tool: OSINTTool, command: str) -> str:
        """Resolve a runnable command to an absolute executable path when possible."""
        resolved = self._which(command, env=self._build_runtime_env(tool))
        if resolved:
            return resolved

        if tool.installation_method == InstallationMethod.GIT and tool.install_path:
            repo_command = Path(tool.install_path) / command
            if repo_command.exists():
                return str(repo_command)

        return command

    def get_tool_runtime_issue(self, tool: OSINTTool) -> Optional[str]:
        """Return a compatibility issue for the configured runtime, if any."""
        managed_tool = self._resolve_tool(tool)
        if not self.needs_python_runtime(managed_tool):
            return None

        runtime_python = self.get_runtime_python()
        if not runtime_python:
            return (
                f"Python {recommended_python_label()} runtime not found. Run bootstrap_runtime.py "
                "or the OSINT Hub Runtime Setup release helper first."
            )

        version = self.get_runtime_python_version()
        if not version:
            return None

        minimum_python = getattr(managed_tool, "minimum_python", None)
        if minimum_python and version[:2] < minimum_python:
            return (
                f"Requires Python {minimum_python[0]}.{minimum_python[1]} or newer, "
                f"but runtime is Python {version[0]}.{version[1]}."
            )

        maximum_python = getattr(managed_tool, "maximum_python", None)
        if maximum_python and version[:2] > maximum_python:
            return (
                f"Supports only up to Python {maximum_python[0]}.{maximum_python[1]}, "
                f"but runtime is Python {version[0]}.{version[1]}."
            )

        return None

    def get_tool_prerequisite_issue(self, tool: OSINTTool) -> Optional[str]:
        """Return missing non-Python prerequisites for a tool, if any."""
        managed_tool = self._resolve_tool(tool)
        missing_commands = self.get_missing_required_commands(managed_tool)
        if missing_commands:
            return f"Missing required command(s): {', '.join(missing_commands)}."
        return None

    def _run_healthcheck(self, tool: OSINTTool) -> tuple[bool, str]:
        """Run an optional lightweight startup check for installed tools."""
        managed_tool = self._resolve_tool(tool)
        cache_key = managed_tool.id
        if cache_key in self._healthcheck_cache:
            return self._healthcheck_cache[cache_key]

        healthcheck_args = getattr(managed_tool, "healthcheck_args", [])
        if not healthcheck_args:
            result = (True, "")
            self._healthcheck_cache[cache_key] = result
            return result

        if managed_tool.installation_method == InstallationMethod.GIT and not managed_tool.install_path:
            result = (True, "")
            self._healthcheck_cache[cache_key] = result
            return result

        cmd = self._command_parts(managed_tool.run_command)
        if not cmd:
            result = (False, "No runtime command configured.")
            self._healthcheck_cache[cache_key] = result
            return result

        if cmd[0] in ("python3", "python"):
            cmd[0] = str(self._require_runtime_python())
        else:
            cmd[0] = self._resolve_command_reference(managed_tool, cmd[0])
        cmd.extend(healthcheck_args)

        run_cwd = None
        if managed_tool.installation_method == InstallationMethod.GIT and managed_tool.install_path:
            install_path = Path(managed_tool.install_path)
            if install_path.exists():
                run_cwd = str(install_path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                cwd=run_cwd,
                env=self._build_runtime_env(managed_tool),
                check=False,
            )
        except Exception as exc:
            outcome = (False, str(exc))
            self._healthcheck_cache[cache_key] = outcome
            return outcome

        combined = (result.stdout or "") + (result.stderr or "")
        output_lines = [line.strip() for line in combined.splitlines() if line.strip()]
        summary = f"exit code {result.returncode}"
        if output_lines:
            summary = output_lines[0]
            if summary.startswith("Traceback") and len(output_lines) > 1:
                for candidate in reversed(output_lines):
                    if candidate.startswith("File "):
                        continue
                    if candidate.startswith("Traceback"):
                        continue
                    summary = candidate
                    break
        passed = result.returncode == 0 or "usage:" in combined.lower() or "options:" in combined.lower()
        outcome = (passed, "" if passed else summary)
        self._healthcheck_cache[cache_key] = outcome
        return outcome

    def check_dependencies(self) -> Tuple[bool, list]:
        """Check if required system dependencies are installed."""
        missing = []

        if not self.get_runtime_python():
            missing.append(f"python {recommended_python_label()} runtime")

        if not self._which("git"):
            missing.append("git")

        if os.name != "nt" and not self._which("gcc") and not self._which("clang"):
            missing.append("gcc or clang (build-essential)")

        return len(missing) == 0, missing

    def current_platform(self) -> str:
        """Return the normalized current platform name used by registry metadata."""
        if sys.platform.startswith("win"):
            return "windows"
        if sys.platform.startswith("darwin"):
            return "macos"
        return "linux"

    def is_tool_supported_on_current_platform(self, tool: OSINTTool) -> bool:
        """Check whether a tool supports the current operating system."""
        managed_tool = self._resolve_tool(tool)
        supported_platforms = getattr(managed_tool, "supported_platforms", [])
        return not supported_platforms or self.current_platform() in supported_platforms

    def can_auto_install(self, tool: OSINTTool) -> bool:
        """Return True when OSINT Hub can install the tool directly."""
        managed_tool = self._resolve_tool(tool)
        if not self.is_tool_supported_on_current_platform(managed_tool):
            return False
        return managed_tool.installation_method in {
            InstallationMethod.PIP,
            InstallationMethod.GIT,
            InstallationMethod.NPM,
            InstallationMethod.DOCKER,
        }

    def get_tool_availability(self, tool: OSINTTool) -> Tuple[str, str]:
        """Return a short availability label and a user-facing explanation."""
        managed_tool = self._resolve_tool(tool)
        note = getattr(managed_tool, "availability_note", "") or ""
        prerequisite_issue = self.get_tool_prerequisite_issue(managed_tool)
        runtime_issue = self.get_tool_runtime_issue(managed_tool)

        if self.check_tool_installed(managed_tool):
            return "READY", "Installed and runnable on this machine."

        if not self.is_tool_supported_on_current_platform(managed_tool):
            message = note or f"Not supported on {self.current_platform()}."
            return "UNSUPPORTED", message

        if prerequisite_issue:
            if note:
                return "SETUP REQUIRED", f"{note} {prerequisite_issue}"
            return "SETUP REQUIRED", prerequisite_issue

        if runtime_issue:
            if not self.get_runtime_python():
                return "SETUP REQUIRED", note or runtime_issue
            if note:
                return "UNSUPPORTED", f"{note} {runtime_issue}"
            return "UNSUPPORTED", runtime_issue

        if not managed_tool.run_command.strip():
            return "DOCS ONLY", note or "This entry is informational only and cannot be run directly yet."

        healthcheck_ok, healthcheck_reason = self._run_healthcheck(managed_tool)
        if not healthcheck_ok and healthcheck_reason:
            message = f"Detected locally but failed startup check: {healthcheck_reason}"
            if self.can_auto_install(managed_tool):
                return "AVAILABLE", message
            return "MANUAL", message

        if self.can_auto_install(managed_tool):
            return "AVAILABLE", "Can be installed from inside OSINT Hub."

        return "MANUAL", note or "Requires manual setup outside OSINT Hub."

    def install_tool(
        self,
        tool: OSINTTool,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Tuple[bool, str]:
        """
        Install a tool.

        Args:
            tool: The OSINT tool to install
            progress_callback: Optional callback(status, progress_percent)

        Returns:
            Tuple of (success, message)
        """
        managed_tool = self._resolve_tool(tool)
        self._invalidate_tool_cache(managed_tool.id)

        try:
            if not self.is_tool_supported_on_current_platform(managed_tool):
                self._copy_runtime_state(managed_tool, tool)
                return False, self.get_install_guide(managed_tool)

            if self.get_tool_prerequisite_issue(managed_tool):
                self._copy_runtime_state(managed_tool, tool)
                return False, self.get_install_guide(managed_tool)

            if not self.can_auto_install(managed_tool):
                self._copy_runtime_state(managed_tool, tool)
                return False, self.get_install_guide(managed_tool)

            if self.needs_python_runtime(managed_tool):
                self._require_runtime_python()

            self._report_progress(progress_callback, f"Installing {managed_tool.name}...", 0)

            if managed_tool.installation_method == InstallationMethod.PIP:
                success, msg = self._install_pip(managed_tool, progress_callback)
            elif managed_tool.installation_method == InstallationMethod.GIT:
                git_target = self.tools_dir / managed_tool.id
                success, msg = self._install_git(managed_tool, progress_callback)
                managed_tool.install_path = str(git_target) if git_target.exists() else ""
            elif managed_tool.installation_method == InstallationMethod.APT:
                success, msg = self._install_apt(managed_tool, progress_callback)
            elif managed_tool.installation_method == InstallationMethod.NPM:
                success, msg = self._install_npm(managed_tool, progress_callback)
            elif managed_tool.installation_method == InstallationMethod.CUSTOM:
                success, msg = self._install_custom(managed_tool, progress_callback)
            elif managed_tool.installation_method == InstallationMethod.DOCKER:
                success, msg = self._install_docker(managed_tool, progress_callback)
            else:
                return False, f"Installation method {managed_tool.installation_method} is not supported yet."

            if not success:
                self._copy_runtime_state(managed_tool, tool)
                return False, msg

            managed_tool.installed = self.check_tool_installed(managed_tool)
            self._copy_runtime_state(managed_tool, tool)

            if not managed_tool.installed:
                self._save_installed_state()
                return (
                    False,
                    f"{msg}. The expected runtime command for {managed_tool.name} was not found afterwards.",
                )

            self._save_installed_state()
            self._report_progress(progress_callback, f"{managed_tool.name} installed successfully!", 100)
            return True, "Installation completed successfully"
        except Exception as e:
            self._copy_runtime_state(managed_tool, tool)
            return False, f"Installation error: {str(e)}"

    def _pip_install_base(self) -> list:
        runtime_python = self._require_runtime_python()
        cmd = [str(runtime_python), "-m", "pip", "install"]
        if not python_is_virtualenv(runtime_python):
            cmd.append("--user")
        if os.name != "nt" and not python_is_virtualenv(runtime_python):
            cmd.append("--break-system-packages")
        return cmd

    def _install_pip(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via pip."""
        try:
            package_spec = tool.install_command.replace("pip install", "", 1).strip()
            if not package_spec:
                return False, "No pip package specified"

            cmd = self._pip_install_base() + self._command_parts(package_spec)
            self._run_command(cmd)
            return True, "Pip installation completed"
        except subprocess.CalledProcessError as e:
            return False, f"Pip install failed: {self._format_subprocess_error(e)}"

    def _install_git(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via git clone."""
        target_dir = self.tools_dir / tool.id
        try:
            parts = self._command_parts(tool.install_command)
            if len(parts) < 3:
                return False, f"Invalid git install command: {tool.install_command}"

            repo_url = parts[2]

            if target_dir.exists():
                self._report_progress(callback, f"Removing previous {tool.name} install...", 10)
                self._remove_tree(target_dir)

            self._run_command(["git", "clone", repo_url, str(target_dir)])

            pip_base = self._pip_install_base()
            requirements_files = [
                target_dir / "requirements.txt",
                target_dir / "REQUIREMENTS",
            ]

            if (target_dir / "setup.py").exists():
                self._run_command(pip_base + ["-e", str(target_dir)])
            elif (target_dir / "pyproject.toml").exists():
                self._run_command(pip_base + [str(target_dir)])

            for requirements_file in requirements_files:
                if requirements_file.exists():
                    self._run_command(pip_base + ["-r", str(requirements_file)])

            return True, "Git clone and dependency installation completed"
        except subprocess.CalledProcessError as e:
            if target_dir.exists():
                try:
                    self._remove_tree(target_dir)
                except RuntimeError:
                    pass
            return False, f"Git clone failed: {self._format_subprocess_error(e)}"

    def _install_apt(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via apt (requires sudo)."""
        if self.check_tool_installed(tool):
            return True, f"{tool.name} is already available on this system"

        install_hint = tool.install_command.replace("sudo ", "", 1)
        return False, f"{tool.name} must be installed manually. Try: {install_hint}"

    def _install_npm(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via npm."""
        try:
            package_name = tool.install_command.replace("npm install -g", "", 1).strip()
            if not package_name:
                return False, "No npm package specified"

            self._run_command(["npm", "install", "-g", package_name])
            return True, "Npm installation completed"
        except subprocess.CalledProcessError as e:
            return False, f"Npm install failed: {self._format_subprocess_error(e)}"

    def _install_custom(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Handle custom/manual installation."""
        if self.check_tool_installed(tool):
            return True, f"{tool.name} is already available on this system"
        return False, self.get_install_guide(tool)

    def _install_docker(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via docker pull."""
        try:
            image_name = tool.install_command.replace("docker pull", "", 1).strip()
            if not image_name:
                return False, "No Docker image specified"

            self._run_command(["docker", "pull", image_name])
            return True, "Docker image pulled"
        except subprocess.CalledProcessError as e:
            return False, f"Docker pull failed: {self._format_subprocess_error(e)}"

    def _run_command(self, cmd: list) -> str:
        """Run a shell command and return output."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=self._build_runtime_env(),
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                output=result.stdout,
                stderr=result.stderr,
            )
        return result.stdout

    def _report_progress(self, callback, message: str, progress: int):
        """Report progress to callback if provided."""
        if callback:
            callback(message, progress)

    def uninstall_tool(self, tool: OSINTTool) -> Tuple[bool, str]:
        """Uninstall a tool."""
        managed_tool = self._resolve_tool(tool)
        self._invalidate_tool_cache(managed_tool.id)

        try:
            if managed_tool.installation_method == InstallationMethod.PIP:
                package_name = managed_tool.install_command.replace("pip install", "", 1).strip().split()[0]
                runtime_python = self._require_runtime_python()
                subprocess.run(
                    [str(runtime_python), "-m", "pip", "uninstall", "-y", package_name],
                    check=True,
                    env=self._build_runtime_env(),
                )
            elif managed_tool.installation_method == InstallationMethod.GIT:
                target_dir = self.tools_dir / managed_tool.id
                if target_dir.exists():
                    self._remove_tree(target_dir)
            elif managed_tool.installation_method == InstallationMethod.NPM:
                package_name = managed_tool.install_command.replace("npm install -g", "", 1).strip().split()[0]
                subprocess.run(
                    ["npm", "uninstall", "-g", package_name],
                    check=True,
                    env=self._build_runtime_env(),
                )

            managed_tool.installed = False
            managed_tool.install_path = ""
            self._copy_runtime_state(managed_tool, tool)
            self._save_installed_state()
            return True, "Uninstalled successfully"
        except Exception as e:
            self._copy_runtime_state(managed_tool, tool)
            return False, f"Uninstall failed: {str(e)}"

    def run_tool(
        self,
        tool: OSINTTool,
        parameters: dict,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[bool, str, str]:
        """
        Run a tool with given parameters with optional real-time output.

        Args:
            tool: The OSINT tool to run
            parameters: Dictionary of parameter values
            output_callback: Function to call with each line of output

        Returns:
            Tuple of (success, stdout, stderr)
        """
        managed_tool = self._resolve_tool(tool)

        try:
            if not self.check_tool_installed(managed_tool):
                return False, "", f"{managed_tool.name} is not installed or its runtime command could not be found."

            self._validate_parameters(managed_tool, parameters)
            cmd = self._build_command(managed_tool, parameters)

            run_cwd = None
            if managed_tool.installation_method == InstallationMethod.GIT and managed_tool.install_path:
                install_path = Path(managed_tool.install_path)
                if install_path.exists():
                    run_cwd = str(install_path)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=run_cwd,
                bufsize=1,
                universal_newlines=True,
                env=self._build_runtime_env(managed_tool),
            )

            stdout_content = []
            while True:
                line = process.stdout.readline() if process.stdout else ""
                if not line and process.poll() is not None:
                    break
                if line:
                    stdout_content.append(line)
                    if output_callback:
                        output_callback(line)

            stdout = "".join(stdout_content)
            if process.returncode != 0:
                return False, stdout, ""

            success, message = self._evaluate_tool_output(managed_tool, stdout)
            if not success:
                return False, stdout, message

            return True, stdout, ""
        except FileNotFoundError as e:
            return False, "", f"Command not found: {e}"
        except ValueError as e:
            return False, "", str(e)
        except Exception as e:
            return False, "", str(e)

    def _validate_parameters(self, tool: OSINTTool, params: dict) -> None:
        missing = []

        for param in tool.parameters:
            value = params.get(param.name)
            if (value is None or str(value).strip() == "") and param.default is None and param.required:
                missing.append(param.name)

        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    def _evaluate_socialscan_output(self, stdout: str) -> tuple[bool, str]:
        """Mark SocialScan runs as failed when every provider lookup is a DNS/network error."""
        error_markers = (
            "clientconnectordnserror",
            "could not contact dns servers",
            "cannot connect to host",
            "name or service not known",
            "temporary failure in name resolution",
        )
        ignored_labels = {"target", "time"}

        result_lines = []
        error_lines = []
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            if line.startswith(("[", "0%", "100%")):
                continue
            if line.startswith("Available,") or line.startswith("Completed "):
                continue

            label, value = line.split(":", 1)
            label = label.strip().lower()
            value = value.strip()
            if not label or label in ignored_labels:
                continue

            result_lines.append(line)
            lowered_value = value.lower()
            if any(marker in lowered_value for marker in error_markers):
                error_lines.append(line)

        if result_lines and len(error_lines) == len(result_lines):
            return (
                False,
                "SocialScan could not reach any provider. This is usually a DNS or outbound HTTPS issue on this PC. "
                f"First error: {error_lines[0]}",
            )

        return True, ""

    def _evaluate_tool_output(self, tool: OSINTTool, stdout: str) -> tuple[bool, str]:
        """Allow tool-specific output validation beyond process exit codes."""
        managed_tool = self._resolve_tool(tool)

        if managed_tool.id == "socialscan":
            return self._evaluate_socialscan_output(stdout)

        return True, ""

    def _build_command(self, tool: OSINTTool, params: dict) -> list:
        """Build command list from tool and parameters."""
        cmd = self._command_parts(tool.run_command)
        if cmd and cmd[0] in ("python3", "python"):
            cmd[0] = str(self._require_runtime_python())
        elif cmd:
            cmd[0] = self._resolve_command_reference(tool, cmd[0])

        for param in tool.parameters:
            value = params.get(param.name)

            if (value is None or str(value).strip() == "") and param.default is not None:
                value = param.default

            if value is None or str(value).strip() == "":
                continue

            if param.type == "boolean":
                if value is True or str(value).lower() == "true":
                    if param.flag:
                        cmd.append(param.flag)
                continue

            if param.flag:
                cmd.append(param.flag)
            cmd.append(str(value))

        return cmd

    def get_install_guide(self, tool: OSINTTool) -> str:
        """Get manual installation instructions for a tool."""
        platform_name = self.current_platform()
        homepage = tool.homepage or "No homepage provided"
        note = getattr(tool, "availability_note", "") or ""

        lines = [f"To install {tool.name}, follow the upstream instructions:"]
        if note:
            lines.append("")
            lines.append(note)
        prerequisite_issue = self.get_tool_prerequisite_issue(tool)
        if prerequisite_issue:
            lines.append("")
            lines.append(prerequisite_issue)
        if self.needs_python_runtime(tool) and not self.get_runtime_python():
            lines.append("")
            lines.append(
                f"Before installing this tool, prepare a Python {recommended_python_label()} runtime with "
                "bootstrap_runtime.py or the OSINT Hub Runtime Setup helper."
            )
        if not self.is_tool_supported_on_current_platform(tool):
            lines.append("")
            lines.append(f"Current OS: {platform_name}. This tool is not marked as supported here.")
        lines.append("")
        lines.append(tool.install_command or "No bundled install command is available.")
        lines.append("")
        lines.append(f"More information: {homepage}")
        return "\n".join(lines)

    def _check_python_target(self, parts: list, install_path: Optional[Path] = None) -> bool:
        if len(parts) <= 1:
            return True

        if parts[1] == "-m" and len(parts) > 2:
            module_name = parts[2]
            if install_path:
                module_dir = install_path / module_name.replace(".", os.sep)
                module_file = install_path / f"{module_name.replace('.', os.sep)}.py"
                return module_dir.exists() or module_file.exists()
            return importlib.util.find_spec(module_name) is not None

        script_path = Path(parts[1])
        if install_path and not script_path.is_absolute():
            script_path = install_path / script_path
        return script_path.exists()

    def _check_command_target(self, parts: list, install_path: Optional[Path] = None) -> bool:
        """Check whether a script/argument referenced by an interpreter command exists."""
        if len(parts) <= 1:
            return True

        target_path = Path(parts[1])
        if install_path and not target_path.is_absolute():
            target_path = install_path / target_path
        return target_path.exists()

    def check_tool_installed(self, tool: OSINTTool) -> bool:
        """Check if a tool runtime is actually available."""
        managed_tool = self._resolve_tool(tool)
        prerequisite_issue = self.get_tool_prerequisite_issue(managed_tool)
        runtime_issue = self.get_tool_runtime_issue(managed_tool)

        if not managed_tool.run_command or not managed_tool.run_command.strip():
            return False

        if prerequisite_issue:
            return False

        if runtime_issue:
            return False

        parts = self._command_parts(managed_tool.run_command)
        if not parts:
            return False

        cmd = parts[0]

        if managed_tool.installation_method == InstallationMethod.GIT:
            if not managed_tool.install_path:
                return False

            install_path = Path(managed_tool.install_path)
            if not install_path.exists():
                return False

            if cmd in ("python3", "python"):
                installed = self._check_python_target(parts, install_path)
                if not installed:
                    return False
                healthcheck_ok, _ = self._run_healthcheck(managed_tool)
                return healthcheck_ok

            if len(parts) > 1 and not self._check_command_target(parts, install_path):
                return False

            resolved = self._which(cmd)
            if resolved:
                healthcheck_ok, _ = self._run_healthcheck(managed_tool)
                return healthcheck_ok

            relative_cmd = install_path / cmd
            if not relative_cmd.exists():
                return False
            healthcheck_ok, _ = self._run_healthcheck(managed_tool)
            return healthcheck_ok

        if cmd in ("python3", "python"):
            installed = self._check_python_target(parts)
            if not installed:
                return False
            healthcheck_ok, _ = self._run_healthcheck(managed_tool)
            return healthcheck_ok

        which_cmd = "python" if os.name == "nt" and cmd == "python3" else cmd
        if self._which(which_cmd) is None:
            return False
        healthcheck_ok, _ = self._run_healthcheck(managed_tool)
        return healthcheck_ok

    def get_tool_version(self, tool: OSINTTool) -> Optional[str]:
        """Get installed version of tool."""
        managed_tool = self._resolve_tool(tool)
        if not self.check_tool_installed(managed_tool):
            return None

        try:
            cmd_list = self._command_parts(managed_tool.run_command)
            if not cmd_list:
                return None

            if cmd_list[0] in ("python3", "python"):
                cmd_list[0] = str(self._require_runtime_python())
            else:
                cmd_list[0] = self._resolve_command_reference(managed_tool, cmd_list[0])
            cmd_list.append("--version")

            run_cwd = None
            if managed_tool.installation_method == InstallationMethod.GIT and managed_tool.install_path:
                install_path = Path(managed_tool.install_path)
                if install_path.exists():
                    run_cwd = str(install_path)

            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=run_cwd,
                env=self._build_runtime_env(managed_tool),
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return None

    def audit_tool(self, tool: OSINTTool) -> dict:
        """Return a serializable audit record for a single tool."""
        managed_tool = self._resolve_tool(tool)
        availability, detail = self.get_tool_availability(managed_tool)
        installed = self.check_tool_installed(managed_tool)
        runtime_issue = self.get_tool_runtime_issue(managed_tool)
        healthcheck_args = list(getattr(managed_tool, "healthcheck_args", []))
        healthcheck_ok = None
        healthcheck_message = ""

        if healthcheck_args:
            try:
                healthcheck_ok, healthcheck_message = self._run_healthcheck(managed_tool)
            except Exception as exc:
                healthcheck_ok = False
                healthcheck_message = str(exc)

        return {
            "id": managed_tool.id,
            "name": managed_tool.name,
            "category": managed_tool.category.value,
            "availability": availability,
            "detail": detail,
            "installed": installed,
            "install_path": managed_tool.install_path or "",
            "install_method": managed_tool.installation_method.value,
            "run_command": managed_tool.run_command,
            "install_command": managed_tool.install_command,
            "homepage": managed_tool.homepage,
            "documentation": managed_tool.documentation,
            "runtime_issue": runtime_issue,
            "supported_platforms": list(getattr(managed_tool, "supported_platforms", [])),
            "healthcheck": {
                "configured": bool(healthcheck_args),
                "args": healthcheck_args,
                "passed": healthcheck_ok,
                "message": healthcheck_message,
            },
            "version": self.get_tool_version(managed_tool) if installed else None,
        }

    def audit_tools(self) -> list[dict]:
        """Return audit records for every registered tool."""
        self.refresh_tool_states(persist=False)
        return [self.audit_tool(tool) for tool in self.registry.get_all_tools()]
