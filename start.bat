@echo off
echo Starting ImageTrim - 图片精简工具...
cd /d "%~dp0"

echo 检查启动环境...

:: 首先尝试使用 uv（推荐）
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用 uv 虚拟环境启动...
    uv run python -m app.main
    pause
    exit /b 0
)

:: 如果没有 uv，尝试激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
    python -m app.main
    pause
    exit /b 0
)

:: 尝试使用py命令（Python启动器）
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用Python启动器...
    py -m app.main
    pause
    exit /b 0
)

:: 尝试使用python3
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用python3...
    python3 -m app.main
    pause
    exit /b 0
)

:: 尝试使用python
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用python...
    python -m app.main
    pause
    exit /b 0
)

:: 如果都找不到，检查是否有其他Python安装
echo 正在搜索Python安装...
for /d %%i in ("C:\Python*" "C:\Program Files\Python*" "C:\Users\%USERNAME%\AppData\Local\Programs\Python\*") do (
    if exist "%%i\python.exe" (
        echo 找到Python: %%i\python.exe
        "%%i\python.exe" -m app.main
        pause
        exit /b 0
    )
)

echo 错误: 未找到Python或uv
echo 您可以：
echo 1. 安装 uv: pip install uv
echo 2. 使用 uv 创建虚拟环境: uv venv
echo 3. 安装系统 Python: https://python.org/downloads/
echo 4. 或者直接运行: uv run python -m app.main
pause