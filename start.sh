#!/bin/bash
# 图片处理工具套件启动脚本 (Linux/Mac)

# 检查Python是否已安装
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python。请先安装Python 3.8或更高版本。"
    exit 1
fi

# 检查依赖包是否已安装
if ! python3 -c "import ttkbootstrap" &> /dev/null
then
    echo "正在安装依赖包..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败。"
        exit 1
    fi
fi

# 启动应用
echo "正在启动图片处理工具套件..."
python3 improved_main_app_v3.py