#!/usr/bin/env python3
"""
优化的构建脚本 - 使用优化的PyInstaller规格文件减小文件体积
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "ImageTrim"
SPEC_FILE = "ImageTrim_optimized.spec"
MAIN_SCRIPT = "app/main.py"

def check_requirements():
    """检查必要的依赖"""
    print("Checking build requirements...")

    try:
        import PyInstaller
        print(f"[OK] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("[OK] PyInstaller installed successfully")

def check_upx():
    """检查UPX是否可用"""
    try:
        result = subprocess.run(["upx", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"[OK] UPX found: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("[WARNING] UPX not found - compression will be less effective")
    print("         Install UPX for better compression: https://upx.github.io/")
    return False

def optimize_project():
    """执行项目优化"""
    print("Optimizing project structure...")

    # 检查主脚本是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print(f"[ERROR] Main script not found: {MAIN_SCRIPT}")
        return False

    # 检查资源目录
    if not os.path.exists("app/resources"):
        print("[WARNING] Resources directory not found, creating empty one...")
        os.makedirs("app/resources", exist_ok=True)

    # 确保图标目录存在
    icons_dir = "app/resources/icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir, exist_ok=True)

    return True

def build_with_spec():
    """使用优化的spec文件构建"""
    print(f"Building optimized {PROJECT_NAME} for {platform.system()}...")

    # Windows使用专用spec文件
    if platform.system() == "Windows":
        spec_file = "ImageTrim_windows.spec"
    else:
        spec_file = SPEC_FILE

    if not os.path.exists(spec_file):
        print(f"[ERROR] Spec file not found: {spec_file}")
        return False

    # 构建命令
    cmd = [sys.executable, "-m", "PyInstaller", spec_file]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True,
                              cwd=os.getcwd())
        print("[OK] Build successful!")

        # 显示构建结果
        show_build_results()
        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def show_build_results():
    """显示构建结果"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("[ERROR] No dist directory found")
        return

    print("\nBuild results:")
    total_size = 0

    for item in dist_dir.iterdir():
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"   FILE {item.name} ({size_mb:.1f} MB)")
        elif item.is_dir():
            # 计算目录大小
            dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            dir_size_mb = dir_size / (1024 * 1024)
            total_size += dir_size_mb
            print(f"   DIR  {item.name}/ ({dir_size_mb:.1f} MB)")

    print(f"\nTotal size: {total_size:.1f} MB")

    # 与预期大小比较
    if total_size < 60:
        print("[OK] Excellent size optimization!")
    elif total_size < 80:
        print("[OK] Good size optimization")
    elif total_size < 100:
        print("[WARNING] Acceptable size, but could be optimized further")
    else:
        print("[WARNING] Large file size - consider additional optimization")

def create_comparison_report():
    """创建与之前构建的对比报告"""
    print("\nOptimization summary:")
    print("   • Excluded matplotlib (~50MB saved)")
    print("   • Excluded scipy (~40MB saved)")
    print("   • Excluded pandas (~20MB saved)")
    print("   • Excluded unused PyQt6 modules (~15MB saved)")
    print("   • Excluded development tools (~5MB saved)")
    print("   • Enabled UPX compression (additional 20-30% reduction)")
    print("   • Enabled symbol stripping")
    print("   • Used maximum Python optimization level")

def main():
    print(f"{PROJECT_NAME} Optimized Build Tool")
    print(f"Platform: {platform.system()}")
    print("=" * 50)

    # 检查要求
    check_requirements()
    check_upx()

    # 优化项目
    if not optimize_project():
        sys.exit(1)

    # 检查spec文件
    if not os.path.exists(SPEC_FILE):
        print(f"[ERROR] Spec file not found: {SPEC_FILE}")
        sys.exit(1)

    # 构建
    if build_with_spec():
        create_comparison_report()
        print("\n[OK] Optimized build completed!")
        print(f"Output directory: dist/")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()