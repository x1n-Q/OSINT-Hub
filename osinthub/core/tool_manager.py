"""
Tool Installation Manager
Handles installation, updates, and dependency management for OSINT tools.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional, Callable
from datetime import datetime
import json

from osinthub.tools.registry import OSINTTool, InstallationMethod, ToolRegistry

class ToolManager:
    """Manages installation and execution of OSINT tools."""

    def __init__(self, tools_dir: str = None, config_dir: str = None):
        self.tools_dir = Path(tools_dir or Path.home() / ".osinthub" / "tools")
        self.config_dir = Path(config_dir or Path.home() / ".osinthub" / "config")
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.registry = ToolRegistry()
        self._load_installed_state()

    def _load_installed_state(self):
        """Load which tools are installed from config."""
        state_file = self.config_dir / "installed.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    installed = json.load(f)
                for tool_id, path in installed.items():
                    tool = self.registry.get_tool(tool_id)
                    if tool:
                        tool.installed = True
                        tool.install_path = path
            except:
                pass

    def _save_installed_state(self):
        """Save installed state to config."""
        state_file = self.config_dir / "installed.json"
        installed = {}
        for tool in self.registry.get_all_tools():
            if tool.installed:
                installed[tool.id] = tool.install_path
        with open(state_file, 'w') as f:
            json.dump(installed, f, indent=2)

    def check_dependencies(self) -> Tuple[bool, list]:
        """Check if required system dependencies are installed."""
        missing = []

        # Check for Python3
        if not shutil.which("python3"):
            missing.append("python3")

        # Check for pip
        if not shutil.which("pip3") and not shutil.which("pip"):
            missing.append("pip3")

        # Check for git
        if not shutil.which("git"):
            missing.append("git")

        # Check for basic build tools
        if not shutil.which("gcc") and not shutil.which("clang"):
            missing.append("gcc or clang (build-essential)")

        return len(missing) == 0, missing

    def install_tool(self, tool: OSINTTool,
                     progress_callback: Optional[Callable[[str, int], None]] = None) -> Tuple[bool, str]:
        """
        Install a tool.

        Args:
            tool: The OSINT tool to install
            progress_callback: Optional callback(status, progress_percent)

        Returns:
            Tuple of (success, message)
        """
        try:
            self._report_progress(progress_callback, f"Installing {tool.name}...", 0)

            if tool.installation_method == InstallationMethod.PIP:
                success, msg = self._install_pip(tool, progress_callback)
            elif tool.installation_method == InstallationMethod.GIT:
                success, msg = self._install_git(tool, progress_callback)
            elif tool.installation_method == InstallationMethod.APT:
                success, msg = self._install_apt(tool, progress_callback)
            elif tool.installation_method == InstallationMethod.NPM:
                success, msg = self._install_npm(tool, progress_callback)
            elif tool.installation_method == InstallationMethod.CUSTOM:
                success, msg = self._install_custom(tool, progress_callback)
            elif tool.installation_method == InstallationMethod.DOCKER:
                success, msg = self._install_docker(tool, progress_callback)
            else:
                return False, f"Installation method {tool.installation_method} not yet implemented"

            if success:
                tool.installed = True
                tool.install_path = str(self.tools_dir / tool.id)
                self._save_installed_state()
                self._report_progress(progress_callback, f"{tool.name} installed successfully!", 100)
                return True, "Installation completed successfully"
            else:
                return False, msg

        except Exception as e:
            return False, f"Installation error: {str(e)}"

    def _install_pip(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via pip."""
        try:
            pkg = tool.install_command.split("pip install ")[1]
            # Add --break-system-packages to handle PEP 668 on modern Linux
            self._run_command(["pip3", "install", "--user", "--break-system-packages", pkg])
            return True, "Pip installation completed"
        except subprocess.CalledProcessError as e:
            return False, f"Pip install failed: {e.stderr or e.stdout or 'Unknown error'}"

    def _install_git(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via git clone."""
        try:
            repo_url = tool.install_command.split("git clone ")[1].split(" ")[0]
            target_dir = self.tools_dir / tool.id

            if target_dir.exists():
                shutil.rmtree(target_dir)

            self._run_command(["git", "clone", repo_url, str(target_dir)])

            # Run any post-install setup
            if (target_dir / "setup.py").exists():
                self._run_command(["pip3", "install", "--user", "--break-system-packages", "-e", str(target_dir)])
            
            # Proactively check for requirements.txt even if setup.py exists
            if (target_dir / "requirements.txt").exists():
                self._run_command(["pip3", "install", "--user", "--break-system-packages", "-r", str(target_dir / "requirements.txt")])
            
            # Support modern pyproject.toml based tools
            if (target_dir / "pyproject.toml").exists():
                self._run_command(["pip3", "install", "--user", "--break-system-packages", str(target_dir)])

            return True, "Git clone and dependency installation completed"
        except subprocess.CalledProcessError as e:
            return False, f"Git clone failed: {e.stderr or e.stdout or 'Unknown error'}"

    def _install_apt(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via apt (requires sudo)."""
        try:
            pkg_name = tool.install_command.split("apt-get install ")[1]
            # We can't use sudo automatically, guide user
            return False, f"Please run: sudo apt-get install {pkg_name}"
        except Exception as e:
            return False, str(e)

    def _install_npm(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via npm."""
        try:
            self._run_command(["npm", "install", "-g", tool.install_command.split("npm install -g ")[1]])
            return True, "Npm installation completed"
        except subprocess.CalledProcessError as e:
            return False, f"Npm install failed: {e.stderr}"

    def _install_custom(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Handle custom installation."""
        return True, "Custom installation - please follow manual steps"

    def _install_docker(self, tool: OSINTTool, callback) -> Tuple[bool, str]:
        """Install tool via docker pull."""
        try:
            image_name = tool.install_command.split("docker pull ")[1]
            self._run_command(["docker", "pull", image_name])
            return True, "Docker image pulled"
        except subprocess.CalledProcessError as e:
            return False, f"Docker pull failed: {e.stderr}"

    def _run_command(self, cmd: list) -> str:
        """Run a shell command and return output."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        return result.stdout

    def _report_progress(self, callback, message: str, progress: int):
        """Report progress to callback if provided."""
        if callback:
            callback(message, progress)

    def uninstall_tool(self, tool: OSINTTool) -> Tuple[bool, str]:
        """Uninstall a tool."""
        try:
            if tool.installation_method == InstallationMethod.PIP:
                pkg_name = tool.install_command.split("pip install ")[1].split()[0]
                subprocess.run(["pip3", "uninstall", "-y", pkg_name], check=True)
            elif tool.installation_method == InstallationMethod.GIT:
                target_dir = self.tools_dir / tool.id
                if target_dir.exists():
                    shutil.rmtree(target_dir)
            elif tool.installation_method == InstallationMethod.NPM:
                pkg_name = tool.install_command.split("npm install -g ")[1].split()[0]
                subprocess.run(["npm", "uninstall", "-g", pkg_name], check=True)

            tool.installed = False
            tool.install_path = ""
            self._save_installed_state()
            return True, "Uninstalled successfully"
        except Exception as e:
            return False, f"Uninstall failed: {str(e)}"

    def run_tool(self, tool: OSINTTool, parameters: dict, 
                 output_callback: Optional[Callable[[str], None]] = None) -> Tuple[bool, str, str]:
        """
        Run a tool with given parameters with optional real-time output.

        Args:
            tool: The OSINT tool to run
            parameters: Dictionary of parameter values
            output_callback: Function to call with each line of output

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            cmd = self._build_command(tool, parameters)
            
            # Only use cwd if it exists
            run_cwd = None
            if tool.install_path and os.path.exists(tool.install_path):
                run_cwd = tool.install_path

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr into stdout for real-time streaming
                text=True,
                cwd=run_cwd,
                bufsize=1,
                universal_newlines=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"} # Force unbuffered output
            )

            stdout_content = []
            
            # Read merged output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    stdout_content.append(line)
                    if output_callback:
                        output_callback(line)
            
            # Return captured content
            stdout = "".join(stdout_content)
            return process.returncode == 0, stdout, ""

        except Exception as e:
            return False, "", str(e)

    def _build_command(self, tool: OSINTTool, params: dict) -> list:
        """Build command list from tool and parameters."""
        # Split base command to handle "python3 script.py" as ["python3", "script.py"]
        cmd = tool.run_command.split()

        for param in tool.parameters:
            value = params.get(param.name)
            if value is not None and str(value).strip() != "":
                if param.type == "boolean":
                    # For booleans, we only add the flag if value is True or "True"
                    if value is True or str(value).lower() == "true":
                        cmd.append(param.flag)
                else:
                    if param.flag:
                        cmd.append(param.flag)
                    cmd.append(str(value))

        return cmd

    def get_install_guide(self, tool: OSINTTool) -> str:
        """Get manual installation instructions for a tool."""
        return f"""
To install {tool.name}:

{tool.install_command}

For more information, visit: {tool.homepage}
"""

    def check_tool_installed(self, tool: OSINTTool) -> bool:
        """Check if a tool binary is available in PATH or its files exist."""
        if not tool.run_command or not tool.run_command.strip():
            return tool.installed
        
        parts = tool.run_command.split()
        cmd = parts[0]
        
        # If it's a python script, check if the script file exists in install_path
        if cmd == "python3" and len(parts) > 1 and tool.install_path:
            script_path = Path(tool.install_path) / parts[1]
            if script_path.exists():
                return True
                
        # Standard check for binary in PATH
        if shutil.which(cmd):
            # If it's in PATH but we also expect an install_path (like for git tools),
            # verify the path exists too
            if tool.installation_method == InstallationMethod.GIT and tool.install_path:
                return Path(tool.install_path).exists()
            return True
            
        return tool.installed and tool.install_path and Path(tool.install_path).exists()

    def get_tool_version(self, tool: OSINTTool) -> Optional[str]:
        """Get installed version of tool."""
        try:
            result = subprocess.run(
                [tool.run_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or result.stderr.strip()
        except:
            return None
