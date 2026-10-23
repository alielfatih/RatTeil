#!/usr/bin/env python
"""
Setup script for RatTeil - Quran Recitation Streaming Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding="utf-8").splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="ratteil",
    version="2024.10.22.1",
    description="Quran recitation streaming tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ali Elfatih",
    author_email="alielfatih@hotmail.com",
    url="https://github.com/alielfatih/RatTeil",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Religious Users",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Topic :: Multimedia :: Audio",
        "Topic :: Religion",
        "Topic :: Internet :: WWW/HTTP :: Streaming",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.25.0",
            "responses>=0.24.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "types-aiohttp>=0.1.0",
            "types-requests>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ratteil=ratteil.cli.main:main",
            "ratteil-legacy=ratteil:ratteil",
        ],
    },
    include_package_data=True,
    package_data={
        "ratteil": ["fixer/*", "imgs/*", "*.json", "*.txt"],
    },
)
