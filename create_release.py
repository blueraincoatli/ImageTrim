#!/usr/bin/env python3
"""
创建GitHub Release的辅助脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== GitHub Release 创建助手 ===")

    # 检查是否在git仓库中
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except:
        print("❌ 错误: 当前目录不是git仓库")
        return

    # 获取当前分支和最新提交
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True, encoding='utf-8')
        latest_commit = result.stdout.strip() if result.stdout else "未知"
        print(f"📝 最新提交: {latest_commit}")
    except:
        latest_commit = "未知"
        print(f"📝 最新提交: {latest_commit}")

    try:
        result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip() if result.stdout else "未知"
        print(f"🌿 当前分支: {current_branch}")
    except:
        current_branch = "未知"
        print(f"🌿 当前分支: {current_branch}")

    # 检查dist目录
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ 错误: dist目录不存在")
        return

    exe_files = list(dist_dir.glob("*.exe"))
    if not exe_files:
        print("❌ 错误: dist目录中没有exe文件")
        return

    print(f"📦 找到exe文件:")
    for exe in exe_files:
        print(f"   - {exe}")

    # Release信息
    print("\n=== Release 信息 ===")
    tag_name = input("🏷️  输入版本标签 (如 v1.0.0): ").strip()
    if not tag_name:
        tag_name = "v1.0.0"

    release_title = input("📰 输入发布标题: ").strip()
    if not release_title:
        release_title = f"ImageTrim {tag_name}"

    print(f"\n📋 Release说明 (输入空行结束):")
    notes_lines = []
    while True:
        line = input()
        if line == "":
            break
        notes_lines.append(line)
    release_notes = "\n".join(notes_lines)

    if not release_notes:
        release_notes = f"""## 🎉 ImageTrim {tag_name} 发布

### ✨ 主要功能
- 图片去重功能
- AVIF格式转换
- 现代化UI界面

### 🐛 修复内容
- 修复打包应用图标显示问题
- 优化网络图片加载性能

### 📦 系统要求
- Windows 10+
- 无需额外依赖

### 🚀 使用方法
1. 下载 ImageTrim.exe
2. 双击运行程序
3. 选择功能开始使用"""

    # 显示摘要
    print(f"\n=== Release 摘要 ===")
    print(f"🏷️  标签: {tag_name}")
    print(f"📰 标题: {release_title}")
    print(f"📁 文件: {[str(f) for f in exe_files]}")
    print(f"📝 说明:\n{release_notes}")

    confirm = input("\n❓ 确认创建Release? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消创建")
        return

    # 创建tag
    print(f"\n🏷️  创建标签 {tag_name}...")
    try:
        subprocess.run(['git', 'tag', tag_name], check=True)
        print(f"✅ 标签创建成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 标签创建失败: {e}")
        return

    # 推送tag
    print(f"📤 推送标签...")
    try:
        subprocess.run(['git', 'push', 'origin', tag_name], check=True)
        print(f"✅ 标签推送成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 标签推送失败: {e}")
        print("💡 请手动推送标签: git push origin", tag_name)
        return

    print(f"\n✅ Release准备完成!")
    print(f"💡 请前往GitHub仓库创建Release:")
    print(f"   1. 打开 https://github.com/blueraincoatli/DeDupImg/releases")
    print(f"   2. 点击 'Create a new release'")
    print(f"   3. 选择标签 {tag_name}")
    print(f"   4. 填写标题和说明")
    print(f"   5. 上传exe文件: {[str(f) for f in exe_files]}")

if __name__ == "__main__":
    main()