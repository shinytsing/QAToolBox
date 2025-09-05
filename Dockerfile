# QAToolBox Docker配置
# 使用Python 3.12官方镜像作为基础镜像
FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=config.settings.production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 基础工具
    build-essential \
    curl \
    wget \
    git \
    # PostgreSQL客户端
    libpq-dev \
    postgresql-client \
    # 图像处理依赖
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    zlib1g-dev \
    # 音频处理依赖
    libsndfile1 \
    ffmpeg \
    # OCR依赖
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    # 浏览器自动化依赖
    chromium \
    chromium-driver \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置Chrome环境变量
ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/bin/chromium

# 复制requirements文件
COPY requirements.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/logs \
    && mkdir -p /app/media \
    && mkdir -p /app/staticfiles \
    && mkdir -p /app/task_storage

# 设置权限
RUN chmod +x /app/manage.py \
    && chmod +x /app/start.sh

# 在构建阶段执行collectstatic
# 设置必要的环境变量以避免数据库连接问题
ENV DB_NAME=temp_db \
    DB_USER=temp_user \
    DB_PASSWORD=temp_password \
    DB_HOST=localhost \
    DB_PORT=5432

# 创建临时数据库文件用于collectstatic
RUN python manage.py migrate --noinput --settings=config.settings.production || true

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 启动命令 - 使用启动脚本
CMD ["./start.sh"]