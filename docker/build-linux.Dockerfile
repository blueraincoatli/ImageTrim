FROM ubuntu:22.04

# 设置非交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libxcb-xinerama0 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY build_cross_platform.py .
COPY app/ ./app/
COPY build/ ./build/

# 创建虚拟环境并安装依赖
RUN uv venv
RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install -r requirements.txt
RUN .venv/bin/pip install pyinstaller

# 构建应用
RUN .venv/bin/python build_cross_platform.py

# 创建输出目录
RUN mkdir -p /output

# 复制构建结果
RUN cp -r dist/ /output/
RUN cp -r archives/ /output/

# 设置入口点
ENTRYPOINT ["bash"]