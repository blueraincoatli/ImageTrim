#!/bin/bash
# 使用 Docker 构建 Linux 版本

echo "🐳 使用 Docker 构建 Linux 版本"
echo "=================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "💡 请安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker 未运行"
    echo "💡 请启动 Docker Desktop"
    exit 1
fi

# 构建 Docker 镜像
echo "🔨 构建 Docker 镜像..."
docker build -t imagetrim-linux-builder -f docker/build-linux.Dockerfile .

# 运行容器并复制构建结果
echo "🚀 运行构建容器..."
docker run --rm -v "$(pwd)/output":/output imagetrim-linux-builder bash -c "
    cp -r /output/* /output/
    chown -R $(id -u):$(id -g) /output
"

echo "✅ Linux 版本构建完成!"
echo "📁 输出文件位置: output/"

# 显示输出文件
if [ -d "output" ]; then
    echo "📦 构建结果:"
    find output -type f -name "*" | head -10
fi