@echo off
REM 图片处理工具套件启动脚本

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请先安装Python 3.8或更高版本。
    pause
    exit /b 1
)

REM 检查依赖包是否已安装
python -c "import ttkbootstrap" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖包安装失败。
        pause
        exit /b 1
    )
)

REM 启动应用
echo 正在启动图片处理工具套件...
python improved_main_app_v3.py

pause