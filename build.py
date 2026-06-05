#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind-CLI 跨平台打包脚本
支持 Windows / macOS / Linux 可执行文件生成
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_platform():
    """获取当前平台"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return system


def check_pyinstaller():
    """检查 PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--break-system-packages'])
    print("✅ PyInstaller 安装完成")


def build_executable():
    """构建可执行文件"""
    plat = get_platform()
    print(f"🚀 开始构建 {plat.upper()} 平台可执行文件...")

    # 清理旧构建
    dist_dir = Path('dist')
    build_dir = Path('build')

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # PyInstaller 参数
    args = [
        sys.executable, '-m', 'PyInstaller',
        '--name', 'documind',
        '--onefile',
        '--clean',
        '--noconfirm',
        '--hidden-import', 'documind.core',
        '--hidden-import', 'documind.cli',
        'documind_cli_entry.py'
    ]

    # Windows 特殊处理
    if plat == 'windows':
        args.extend(['--console'])

    print(f"📝 执行命令: {' '.join(args)}")
    subprocess.check_call(args)

    # 检查输出
    exe_name = 'documind.exe' if plat == 'windows' else 'documind'
    exe_path = dist_dir / exe_name

    if exe_path.exists():
        size = exe_path.stat().st_size
        print(f"✅ 构建成功: {exe_path}")
        print(f"📊 文件大小: {size / 1024 / 1024:.1f} MB")
        return str(exe_path)
    else:
        print("❌ 构建失败: 未找到输出文件")
        return None


def create_release_package():
    """创建发布包"""
    plat = get_platform()
    version = '1.0.0'

    # 构建可执行文件
    exe_path = build_executable()
    if not exe_path:
        return False

    # 创建发布目录
    release_name = f"documind-v{version}-{plat}-{platform.machine()}"
    release_dir = Path('releases') / release_name
    release_dir.mkdir(parents=True, exist_ok=True)

    # 复制文件
    shutil.copy(exe_path, release_dir / Path(exe_path).name)

    # 复制 README
    if Path('README.md').exists():
        shutil.copy('README.md', release_dir / 'README.md')

    # 创建压缩包
    archive_path = shutil.make_archive(
        str(release_dir),
        'zip' if plat == 'windows' else 'gztar',
        str(release_dir)
    )

    print(f"📦 发布包已创建: {archive_path}")
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("🦞 DocuMind-CLI 跨平台打包工具")
    print("=" * 50)

    # 检查 PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()

    # 构建
    if len(sys.argv) > 1 and sys.argv[1] == '--release':
        create_release_package()
    else:
        build_executable()


if __name__ == '__main__':
    main()
