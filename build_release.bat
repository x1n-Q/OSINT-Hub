@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PYTHON=%ROOT%.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%ROOT%build_exe.py" %*
) else (
    python "%ROOT%build_exe.py" %*
)
