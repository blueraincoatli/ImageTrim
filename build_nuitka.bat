@echo off
REM ImageTrim Nuitka 构建脚本 (Windows)
REM 使用 Nuitka 编译为原生可执行文件

echo ========================================
echo   ImageTrim Nuitka 构建工具
echo ========================================
echo.

REM 检查 UV
echo [初始化] 检查环境...
set USE_UV=0
uv --version >nul 2>&1
if not errorlevel 1 (
    if exist uv.lock (
        echo [信息] 检测到 UV 环境
        set USE_UV=1
        set PYTHON_CMD=uv run python
    )
)

if %USE_UV%==0 (
    if exist .venv\Scripts\python.exe (
        echo [信息] 检测到虚拟环境 .venv
        set PYTHON_CMD=.venv\Scripts\python.exe
    ) else (
        echo [信息] 使用系统 Python
        set PYTHON_CMD=python
    )
)

echo [信息] Python 命令: %PYTHON_CMD%
echo.

REM 运行 Python 构建脚本
%PYTHON_CMD% build_nuitka.py

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    pause
    exit /b 1
)

echo.
pause

