#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind-CLI 安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="documind-cli",
    version="1.0.0",
    author="DocuMind Team",
    author_email="documind@example.com",
    description="轻量级本地文档智能分析与知识提取引擎 | Lightweight Local Document Intelligent Analysis Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/documind-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "documind=documind.cli:main",
        ],
    },
    keywords="document analysis knowledge extraction nlp cli text mining",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/documind-cli/issues",
        "Source": "https://github.com/yourusername/documind-cli",
    },
)
