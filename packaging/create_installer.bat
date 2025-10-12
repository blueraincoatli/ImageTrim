@echo off
echo ====================================
echo   ImageTrim 安装程序创建脚本
echo ====================================
echo.

cd /d "%~dp0.."

echo 检查 Inno Setup 是否安装...
where iscc >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Inno Setup 编译器
    echo.
    echo 请下载并安装 Inno Setup:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo 安装完成后，重新运行此脚本
    pause
    exit /b 1
)

echo 创建版本信息文件...
echo 文件版本=1.0.0
echo 产品版本=1.0.0
echo 文件描述=ImageTrim - 图片精简工具
echo 公司名称=BlueRainCoat
echo 合法版权=Copyright (c) 2025 BlueRainCoat
echo 原始文件名=ImageTrim.exe
echo 产品名称=ImageTrim > packaging\windows\version_info.txt

echo 开始编译安装程序...
iscc packaging\windows\installer.iss

if %errorlevel% equ 0 (
    echo.
    echo ✅ 安装程序创建成功！
    echo 📁 输出位置: dist\ImageTrim-1.0.0-installer.exe
) else (
    echo.
    echo ❌ 安装程序创建失败
    echo 请检查 installer.iss 文件配置
)

echo.
pause