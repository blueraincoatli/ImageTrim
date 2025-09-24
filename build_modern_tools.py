#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代图片处理工具套件 - 打包和部署脚本
支持插件化架构的多种打包模式
"""

import os
import sys
import subprocess
import shutil
import json
import time
from datetime import datetime
import zipfile
import hashlib

class PackageBuilder:
    """现代图片处理工具套件打包器"""

    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.project_root, "dist")
        self.build_dir = os.path.join(self.project_root, "build")
        self.main_script = "modern_ui_framework.py"
        self.version = "1.0.0"
        self.app_name = "ModernImageTools"

        # 依赖列表
        self.dependencies = [
            "Pillow",
            "pillow-avif-plugin",
            "numpy",
            "psutil",
            "ttkbootstrap"
        ]

        # 构建配置
        self.build_configs = {
            "single_file": {
                "name": f"{self.app_name}_SingleFile",
                "args": ["--onefile", "--windowed"],
                "description": "单文件可执行程序"
            },
            "directory": {
                "name": f"{self.app_name}_Directory",
                "args": ["--onedir", "--windowed"],
                "description": "目录版本（启动更快）"
            },
            "console": {
                "name": f"{self.app_name}_Console",
                "args": ["--onefile", "--console"],
                "description": "控制台版本（调试用）"
            },
            "portable": {
                "name": f"{self.app_NAME}_Portable",
                "args": ["--onedir", "--windowed", "--add-data=docs;docs"],
                "description": "便携版本（包含文档）"
            }
        }

    def clean_build_artifacts(self):
        """清理构建产物"""
        print("清理构建产物...")
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        # 清理其他临时文件
        temp_files = ["*.spec", "*.pyc", "__pycache__", "*.pyo", "*.pyd"]
        for pattern in temp_files:
            for item in os.listdir(self.project_root):
                if pattern.endswith("*") and item.startswith(pattern[:-1]):
                    path = os.path.join(self.project_root, item)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                elif item == pattern:
                    path = os.path.join(self.project_root, item)
                    if os.path.exists(path):
                        os.remove(path)

    def check_dependencies(self):
        """检查依赖是否安装"""
        print("检查依赖...")
        missing_deps = []

        for dep in self.dependencies:
            try:
                if dep == "pillow-avif-plugin":
                    import pillow_avif
                else:
                    __import__(dep.lower().replace("-", "_"))
                print(f"✓ {dep}")
            except ImportError:
                missing_deps.append(dep)
                print(f"✗ {dep} (缺失)")

        if missing_deps:
            print(f"\n缺失依赖: {', '.join(missing_deps)}")
            print("请使用以下命令安装:")
            print(f"pip install {' '.join(missing_deps)}")
            return False

        return True

    def create_version_info(self):
        """创建版本信息文件"""
        version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({self.version.split(".")[0]}, {self.version.split(".")[1]}, {self.version.split(".")[2]}, 0),
    prodvers=({self.version.split(".")[0]}, {self.version.split(".")[1]}, {self.version.split(".")[2]}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Modern Image Tools'),
           StringStruct(u'FileDescription', u'现代图片处理工具套件'),
           StringStruct(u'FileVersion', u'{self.version}'),
           StringStruct(u'InternalName', u'{self.app_name}'),
           StringStruct(u'LegalCopyright', u'Copyright © 2024'),
           StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
           StringStruct(u'ProductName', u'{self.app_name}'),
           StringStruct(u'ProductVersion', u'{self.version}')])
      ])
  ]
)
'''
        return version_info

    def create_main_entry_point(self):
        """创建主入口文件"""
        main_py = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代图片处理工具套件 - 主入口点
自动检测和启动合适的界面
"""

import sys
import os

def main():
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    try:
        # 尝试导入现代UI框架
        from modern_ui_framework import main as modern_main
        print("启动现代UI框架...")
        modern_main()
    except ImportError as e:
        print(f"无法导入现代UI框架: {{e}}")
        print("尝试启动传统UI框架...")

        # 回退到传统UI
        try:
            from ImageDedupUI_Confidence import ConfidenceImageDedupUI
            import tkinter as tk

            root = tk.Tk()
            app = ConfidenceImageDedupUI(root)
            root.mainloop()
        except ImportError as e2:
            print(f"无法导入传统UI框架: {{e2}}")
            print("请确保项目文件完整")
            sys.exit(1)
        except Exception as e2:
            print(f"启动传统UI框架失败: {{e2}}")
            sys.exit(1)

if __name__ == "__main__":
    main()
'''
        return main_py

    def build_package(self, config_name: str):
        """构建指定配置的包"""
        if config_name not in self.build_configs:
            print(f"错误: 未知配置 {config_name}")
            return False

        config = self.build_configs[config_name]
        print(f"开始构建: {config['description']}")

        # 创建临时主文件
        temp_main = "temp_main.py"
        with open(temp_main, "w", encoding="utf-8") as f:
            f.write(self.create_main_entry_point())

        try:
            # 基础PyInstaller命令
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--name=" + config["name"],
                "--clean",
                "--workpath=" + self.build_dir,
                "--distpath=" + self.dist_dir,
            ]

            # 添加配置特定的参数
            cmd.extend(config["args"])

            # 添加数据文件
            data_files = [
                ("*.json", "."),
                ("docs/*.md", "docs"),
                ("*.txt", ".")
            ]

            for pattern, dest in data_files:
                cmd.extend(["--add-data", f"{pattern};{dest}"])

            # 添加主脚本
            cmd.append(temp_main)

            print(f"构建命令: {' '.join(cmd)}")

            # 运行构建
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ 构建成功: {config['description']}")
                print(result.stdout)
                return True
            else:
                print(f"✗ 构建失败: {config['description']}")
                print("错误信息:")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"构建过程中发生错误: {e}")
            return False
        finally:
            # 清理临时文件
            if os.path.exists(temp_main):
                os.remove(temp_main)

    def create_installer(self):
        """创建安装程序"""
        print("创建安装程序...")

        # 创建ZIP包
        zip_path = os.path.join(self.dist_dir, f"{self.app_name}_v{self.version}_Portable.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加目录版本
            directory_path = os.path.join(self.dist_dir, f"{self.app_name}_Directory")
            if os.path.exists(directory_path):
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, directory_path)
                        zipf.write(file_path, os.path.join(self.app_name, arcname))

            # 添加文档
            docs_path = os.path.join(self.project_root, "docs")
            if os.path.exists(docs_path):
                for root, dirs, files in os.walk(docs_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.project_root)
                            zipf.write(file_path, arcname)

            # 添加README和配置文件
            readme_content = f"""# {self.app_name} v{self.version}

现代图片处理工具套件

## 功能特性
- 图片去重：智能识别重复和相似图片
- AVIF转换：高效图片格式转换
- 批量重命名：支持多种重命名规则
- 图片优化：智能优化图片质量和大小

## 系统要求
- Windows 7/8/10/11
- 64位系统
- 至少100MB可用空间

## 使用方法
1. 解压ZIP文件
2. 进入程序目录
3. 运行 {self.app_name}_Directory.exe

## 更新日志
v{self.version} - 首次发布
- 插件化架构
- 现代化UI界面
- 配置持久化
- 性能优化

## 技术支持
如有问题，请查阅docs目录下的文档。
"""

            zipf.writestr("README.txt", readme_content)

            version_info_content = f"""版本信息:
应用名称: {self.app_name}
版本号: {self.version}
构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
构建类型: Portable
"""

            zipf.writestr("VERSION.txt", version_info_content)

        print(f"✓ 便携包已创建: {zip_path}")
        return zip_path

    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def generate_build_report(self):
        """生成构建报告"""
        report = {
            "version": self.version,
            "build_time": datetime.now().isoformat(),
            "build_configs": {},
            "files": {}
        }

        # 收集构建的文件信息
        if os.path.exists(self.dist_dir):
            for config_name, config in self.build_configs.items():
                config_path = os.path.join(self.dist_dir, config["name"])
                if os.path.exists(config_path):
                    if os.path.isfile(config_path):
                        file_size = os.path.getsize(config_path)
                        file_hash = self.calculate_file_hash(config_path)
                        report["files"][config_name] = {
                            "type": "file",
                            "size": file_size,
                            "hash": file_hash,
                            "path": config_path
                        }
                    elif os.path.isdir(config_path):
                        total_size = 0
                        file_count = 0
                        for root, dirs, files in os.walk(config_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                        report["files"][config_name] = {
                            "type": "directory",
                            "size": total_size,
                            "file_count": file_count,
                            "path": config_path
                        }

        # 保存报告
        report_path = os.path.join(self.dist_dir, "build_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✓ 构建报告已生成: {report_path}")
        return report_path

    def build_all(self):
        """构建所有配置"""
        print(f"开始构建 {self.app_name} v{self.version}...")

        # 检查依赖
        if not self.check_dependencies():
            return False

        # 清理构建产物
        self.clean_build_artifacts()

        # 构建所有配置
        successful_builds = []
        for config_name in self.build_configs.keys():
            if self.build_package(config_name):
                successful_builds.append(config_name)

        # 创建安装包
        if "directory" in successful_builds:
            self.create_installer()

        # 生成构建报告
        self.generate_build_report()

        # 显示结果
        print(f"\n构建完成!")
        print(f"成功构建 {len(successful_builds)} 个配置:")
        for config_name in successful_builds:
            config = self.build_configs[config_name]
            print(f"  ✓ {config['name']} - {config['description']}")

        print(f"\n输出目录: {self.dist_dir}")
        return True

def main():
    """主函数"""
    builder = PackageBuilder()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "clean":
            builder.clean_build_artifacts()
            print("清理完成!")
        elif command == "deps":
            builder.check_dependencies()
        elif command in builder.build_configs:
            builder.build_package(command)
        elif command == "all":
            builder.build_all()
        else:
            print(f"未知命令: {command}")
            print("可用命令: clean, deps, all, " + ", ".join(builder.build_configs.keys()))
    else:
        # 默认构建所有配置
        builder.build_all()

if __name__ == "__main__":
    main()