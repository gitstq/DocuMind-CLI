#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind-CLI 独立入口文件（用于PyInstaller打包）
"""

import sys
import os

# 确保模块路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from documind.cli import main

if __name__ == '__main__':
    main()
