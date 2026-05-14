#!/usr/bin/env python3
"""
OSINT Hub Setup - Pip Installable
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="osinthub",
    version="1.0.0",
    author="OSINT Hub Team",
    author_email="contact@osinthub.local",
    description="All-in-One OSINT Framework with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x1n-Q/OSINT-Hub",
    packages=find_packages(),
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
    ],
    entry_points={
        "console_scripts": [
            "osinthub=main:main",
            "osinthub-cli=cli:main",
            "osinthub-gui=gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
)
