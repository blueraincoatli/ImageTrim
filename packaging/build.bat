@echo off
echo ====================================
echo   ImageTrim Windows 打包脚本
echo ====================================
echo.

cd /d "%~dp0.."

echo 🧹 清理构建目录...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo 📦 安装构建工具...
python -m pip install --upgrade pip
pip install pyinstaller setuptools wheel

echo 🪟 开始构建 Windows 版本...
python packaging/build.py

echo.
echo ✅ 构建完成！
echo 📁 输出文件位置：
echo    - 便携版: dist\ImageTrim-*-windows-portable.zip
echo    - 安装程序: dist\ImageTrim-*-installer.exe
echo.
echo 📋 下一步：
echo    1. 检查输出文件是否正常生成
echo    2. 使用 Inno Setup 编译 installer.iss 文件
echo    3. 测试安装和运行
echo.

pause