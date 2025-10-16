#!/usr/bin/env python3
"""
ImageTrim Nuitka 构建脚本
使用 Nuitka 编译为原生可执行文件

使用方法:
  python build_nuitka.py          # 完整编译模式（单文件 exe，20-25 分钟）
  python build_nuitka.py --fast   # 快速编译模式（文件夹，2-5 分钟）
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
PROJECT_NAME = "ImageTrim"
ENTRY_POINT = "app/main.py"
OUTPUT_DIR = "dist_nuitka"
OUTPUT_DIR_FAST = "dist_nuitka_fast"  # 快速编译模式的输出目录
ICON_PATH = "app/resources/icons/imageTrim256px.ico"
RESOURCES_DIR = "app/resources"

# UV 配置
USE_UV = True
VENV_PATH = ".venv"

# 检查是否使用快速编译模式
FAST_MODE = "--fast" in sys.argv


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num, text):
    """打印步骤"""
    print(f"\n[步骤 {step_num}] {text}")


def check_uv():
    """检查 UV 是否可用"""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ UV 可用: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("   ℹ️  UV 未安装")
    return False


def get_python_command():
    """获取正确的 Python 命令"""
    
    # 方法 1: 检查是否使用 UV
    if USE_UV:
        has_uv = check_uv()
        if has_uv and os.path.exists("uv.lock"):
            print("   ✅ 使用 UV 虚拟环境")
            return ["uv", "run", "python"]
    
    # 方法 2: 检查是否在虚拟环境中
    if os.path.exists(VENV_PATH):
        if sys.platform == "win32":
            venv_python = os.path.join(VENV_PATH, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(VENV_PATH, "bin", "python")
        
        if os.path.exists(venv_python):
            print(f"   ✅ 使用虚拟环境: {VENV_PATH}")
            return [venv_python]
    
    # 方法 3: 使用当前 Python
    print(f"   ℹ️  使用当前 Python: {sys.executable}")
    return [sys.executable]


def check_nuitka(python_cmd):
    """检查 Nuitka 是否安装"""
    print_step(1, "检查 Nuitka")
    
    try:
        result = subprocess.run(
            python_cmd + ["-m", "nuitka", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"   ✅ {version}")
            return True
    except Exception:
        pass
    
    print("   ❌ Nuitka 未安装")
    print("   请运行: pip install nuitka")
    return False


def check_compiler():
    """检查 C 编译器"""
    print_step(2, "检查 C 编译器")

    if sys.platform == "win32":
        # 方法 1: 检查 Visual Studio 安装路径
        vs_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022",
            r"C:\Program Files\Microsoft Visual Studio\2019",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019",
        ]

        for vs_path in vs_paths:
            if os.path.exists(vs_path):
                # 查找具体版本
                for edition in ["Community", "Professional", "Enterprise"]:
                    cl_path = os.path.join(vs_path, edition, "VC", "Tools", "MSVC")
                    if os.path.exists(cl_path):
                        # 获取版本号
                        versions = [d for d in os.listdir(cl_path) if os.path.isdir(os.path.join(cl_path, d))]
                        if versions:
                            latest_version = sorted(versions)[-1]
                            print(f"   ✅ Visual Studio {os.path.basename(vs_path)} ({edition}) 已安装")
                            print(f"      MSVC 版本: {latest_version}")
                            print(f"      Nuitka 会自动使用 MSVC 编译器")
                            return True

        # 方法 2: 检查 vswhere (Visual Studio 官方工具)
        vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
        if os.path.exists(vswhere_path):
            try:
                result = subprocess.run(
                    [vswhere_path, "-latest", "-property", "installationPath"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    vs_install_path = result.stdout.strip()
                    print(f"   ✅ Visual Studio 已安装")
                    print(f"      路径: {vs_install_path}")
                    print(f"      Nuitka 会自动使用 MSVC 编译器")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # 方法 3: 检查 MinGW
        try:
            result = subprocess.run(
                ["gcc", "--version"],
                capture_output=True,
                timeout=5
            )
            print("   ✅ MinGW GCC 可用")
            print("      Nuitka 会使用 MinGW 编译器")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 如果都没找到，Nuitka 会自动下载
        print("   ⚠️  未检测到已安装的 C 编译器")
        print("      Nuitka 会自动下载 MinGW (仅首次需要，约 5-10 分钟)")
        print("      后续编译会复用已下载的编译器")
        return True  # 继续，让 Nuitka 处理
    else:
        # Linux/Mac
        try:
            result = subprocess.run(
                ["gcc", "--version"],
                capture_output=True,
                timeout=5
            )
            print("   ✅ GCC 可用")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("   ❌ GCC 未安装")
            return False


def check_resources():
    """检查资源文件"""
    print_step(3, "检查资源文件")
    
    if not os.path.exists(ENTRY_POINT):
        print(f"   ❌ 入口文件不存在: {ENTRY_POINT}")
        return False
    print(f"   ✅ 入口文件: {ENTRY_POINT}")
    
    if not os.path.exists(ICON_PATH):
        print(f"   ⚠️  图标文件不存在: {ICON_PATH}")
    else:
        print(f"   ✅ 图标文件: {ICON_PATH}")
    
    if not os.path.exists(RESOURCES_DIR):
        print(f"   ⚠️  资源目录不存在: {RESOURCES_DIR}")
    else:
        print(f"   ✅ 资源目录: {RESOURCES_DIR}")
    
    return True


def clean_output_dir():
    """清理输出目录"""
    print_step(4, "清理输出目录")

    # 根据编译模式选择输出目录
    output_dir = OUTPUT_DIR_FAST if FAST_MODE else OUTPUT_DIR

    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            print(f"   ✅ 已删除: {output_dir}")
        except Exception as e:
            print(f"   ⚠️  删除失败: {e}")

    # 清理 Nuitka 缓存（可选）
    nuitka_cache = f"{ENTRY_POINT}.build"
    if os.path.exists(nuitka_cache):
        print(f"   ℹ️  保留 Nuitka 缓存以加速后续编译: {nuitka_cache}")

    return True


def build_with_nuitka(python_cmd):
    """使用 Nuitka 构建"""
    print_step(5, "开始 Nuitka 编译")

    # 根据编译模式显示不同的提示
    if FAST_MODE:
        print("\n   ⚡ 快速编译模式 (开发测试用)")
        print("   - 编译时间: 2-5 分钟")
        print("   - 输出格式: 文件夹 (非单文件)")
        print("   - 优化级别: 标准 (无 LTO)")
        print("   - 输出目录: dist_nuitka_fast/")
        print("\n   💡 提示: 发布时请使用完整编译模式 (不加 --fast 参数)")
    else:
        print("\n   📦 完整编译模式 (发布用)")
        print("   - 编译时间: 20-25 分钟")
        print("   - 输出格式: 单文件 exe")
        print("   - 优化级别: 最高 (LTO)")
        print("   - 输出目录: dist_nuitka/")
        print("\n   💡 提示: 开发测试时可使用快速模式 (--fast 参数)")

    print("\n   🚀 开始编译，请耐心等待...\n")

    # 构建 Nuitka 命令
    cmd = python_cmd + ["-m", "nuitka"]

    # 基本参数
    cmd.extend([
        "--standalone",           # 独立模式
        "--assume-yes-for-downloads",  # 自动下载依赖
    ])

    # 根据模式添加不同的参数
    if not FAST_MODE:
        cmd.append("--onefile")  # 单文件模式（仅完整编译）
    
    # 插件
    cmd.extend([
        "--enable-plugin=pyqt6",  # PyQt6 插件
    ])

    # 包含 pillow-avif-plugin 模块（关键！）
    cmd.extend([
        "--include-package=pillow_avif",  # 包含整个 pillow_avif 包
        "--include-module=pillow_avif._avif",  # 包含 C 扩展模块
    ])
    print("   📦 包含 pillow-avif-plugin 支持")

    # 包含 send2trash 模块（用于删除原图功能）
    cmd.extend([
        "--include-package=send2trash",  # 包含 send2trash 包
    ])
    print("   📦 包含 send2trash 支持")
    
    # 资源文件 - 分别包含 icons 和 images 目录
    icons_dir = os.path.join(RESOURCES_DIR, "icons")
    images_dir = os.path.join(RESOURCES_DIR, "images")

    if os.path.exists(icons_dir):
        cmd.append(f"--include-data-dir={icons_dir}=resources/icons")
        print(f"   📦 包含图标目录: {icons_dir}")

    if os.path.exists(images_dir):
        cmd.append(f"--include-data-dir={images_dir}=resources/images")
        print(f"   📦 包含图片目录: {images_dir}")
    
    # Windows 特定参数
    if sys.platform == "win32":
        cmd.extend([
            "--windows-disable-console",  # 禁用控制台窗口
        ])
        if os.path.exists(ICON_PATH):
            cmd.append(f"--windows-icon-from-ico={ICON_PATH}")

    # 优化参数（仅完整编译模式）
    if not FAST_MODE:
        cmd.extend([
            "--lto=yes",              # 链接时优化（慢但生成更优化的代码）
        ])

    cmd.extend([
        "--remove-output",        # 删除中间文件
    ])

    # 输出参数
    output_dir = OUTPUT_DIR_FAST if FAST_MODE else OUTPUT_DIR
    cmd.extend([
        f"--output-dir={output_dir}",
        f"--output-filename={PROJECT_NAME}.exe" if sys.platform == "win32" else f"--output-filename={PROJECT_NAME}",
    ])
    
    # 入口文件
    cmd.append(ENTRY_POINT)
    
    # 打印命令
    print("   命令:")
    print(f"   {' '.join(cmd)}\n")
    
    # 执行编译
    start_time = datetime.now()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时显示输出
        for line in process.stdout:
            print(f"   {line.rstrip()}")
        
        process.wait()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if process.returncode == 0:
            print(f"\n   ✅ 编译成功! 耗时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
            return True
        else:
            print(f"\n   ❌ 编译失败 (退出码: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"\n   ❌ 编译过程出错: {e}")
        return False


def analyze_output():
    """分析输出文件"""
    print_step(6, "分析输出文件")

    output_dir = OUTPUT_DIR_FAST if FAST_MODE else OUTPUT_DIR

    if FAST_MODE:
        # 快速模式：检查文件夹（Nuitka 使用入口文件名作为文件夹名）
        entry_name = os.path.splitext(os.path.basename(ENTRY_POINT))[0]  # "main"
        if sys.platform == "win32":
            exe_path = os.path.join(output_dir, f"{entry_name}.dist", f"{PROJECT_NAME}.exe")
        else:
            exe_path = os.path.join(output_dir, f"{entry_name}.dist", PROJECT_NAME)
    else:
        # 完整模式：检查单文件
        if sys.platform == "win32":
            exe_path = os.path.join(output_dir, f"{PROJECT_NAME}.exe")
        else:
            exe_path = os.path.join(output_dir, PROJECT_NAME)

    if not os.path.exists(exe_path):
        print(f"   ❌ 可执行文件不存在: {exe_path}")
        return False
    
    # 文件大小
    if FAST_MODE:
        # 快速模式：计算整个文件夹大小
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(os.path.dirname(exe_path)):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        size_bytes = total_size
        size_mb = size_bytes / (1024 * 1024)

        print(f"   ✅ 可执行文件: {exe_path}")
        print(f"   📦 文件夹大小: {size_mb:.1f} MB ({size_bytes:,} 字节)")
        print(f"\n   💡 运行方式: 直接运行 {exe_path}")
    else:
        # 完整模式：单文件大小
        size_bytes = os.path.getsize(exe_path)
        size_mb = size_bytes / (1024 * 1024)

        print(f"   ✅ 可执行文件: {exe_path}")
        print(f"   📦 文件大小: {size_mb:.1f} MB ({size_bytes:,} 字节)")

        # 与 PyInstaller 对比
        pyinstaller_exe = os.path.join("dist", f"{PROJECT_NAME}.exe")
        if os.path.exists(pyinstaller_exe):
            pyinstaller_size = os.path.getsize(pyinstaller_exe) / (1024 * 1024)
            reduction = ((pyinstaller_size - size_mb) / pyinstaller_size) * 100
            print(f"\n   📊 与 PyInstaller 对比:")
            print(f"   - PyInstaller: {pyinstaller_size:.1f} MB")
            print(f"   - Nuitka:      {size_mb:.1f} MB")
            print(f"   - 减少:        {reduction:.1f}%")

    return True


def main():
    """主函数"""
    print_header(f"{PROJECT_NAME} Nuitka 构建工具")
    
    # 获取 Python 命令
    print("\n[初始化] 检测 Python 环境...")
    python_cmd = get_python_command()
    print(f"   使用命令: {' '.join(python_cmd)}\n")
    
    # 执行构建流程
    steps = [
        ("检查 Nuitka", lambda: check_nuitka(python_cmd)),
        ("检查 C 编译器", check_compiler),
        ("检查资源文件", check_resources),
        ("清理输出目录", clean_output_dir),
        ("Nuitka 编译", lambda: build_with_nuitka(python_cmd)),
        ("分析输出文件", analyze_output),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ 构建失败: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("  ✅ Nuitka 编译完成!")
    print("=" * 70)
    print(f"\n  可执行文件: {OUTPUT_DIR}\\{PROJECT_NAME}.exe")
    print("\n  下一步:")
    print(f"  1. 测试: {OUTPUT_DIR}\\{PROJECT_NAME}.exe")
    print("  2. 对比启动速度和运行性能")
    print("  3. 如有问题，可以回退到 PyInstaller 版本\n")


if __name__ == "__main__":
    main()

