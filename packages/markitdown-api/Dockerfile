# MarkItDown API Docker 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1000 appuser

# 复制依赖文件
COPY pyproject.toml ./
COPY src/ ./src/

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["markitdown-api", "--host", "0.0.0.0", "--port", "8000", "--production"]
