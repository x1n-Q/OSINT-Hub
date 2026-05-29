#!/usr/bin/env python3
"""
OSINT Hub Setup - Pip Installable
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="osinthub",
    version="1.0.3",
    author="Daniel Depaor",
    author_email="daniel.depaor@outlook.jp",
    description="All-in-One OSINT Framework with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x1n-Q/OSINT-Hub",
    packages=find_packages(),
    py_modules=[
        "main",
        "cli",
        "menu",
        "check_system",
        "first_run",
        "setup_complete",
        "test_system",
        "bootstrap_env",
        "bootstrap_runtime",
        "tool_audit",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.2.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
        "pyyaml>=6.0.1",
        "ttkthemes>=3.2.2",
    ],
    entry_points={
        "console_scripts": [
            "osinthub=main:main",
            "osinthub-cli=cli:main",
            "osinthub-gui=main:main",
            "osinthub-bootstrap=bootstrap_env:main",
            "osinthub-runtime-setup=bootstrap_runtime:main",
            "osinthub-audit=tool_audit:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
)
