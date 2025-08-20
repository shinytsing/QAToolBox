# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements/ /app/requirements/

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/logs /app/media /app/staticfiles

# 设置权限
RUN chmod +x /app/scripts/start_with_tests.sh

# 创建非root用户
RUN useradd --create-home --shell /bin/bash qatoolbox && \
    chown -R qatoolbox:qatoolbox /app

# 切换到非root用户
USER qatoolbox

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/tools/health/ || exit 1

# 启动命令
CMD ["/app/scripts/start_with_tests.sh", "production"] 