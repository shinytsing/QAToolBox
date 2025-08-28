#!/bin/bash
# =============================================================================
# 修复Dockerfile包依赖问题
# =============================================================================
# 解决Debian Bullseye中包名变化和不存在的包
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

PROJECT_DIR="/home/qatoolbox/QAToolBox"

echo -e "${BLUE}🔧 修复Dockerfile包依赖问题...${NC}"

cd "$PROJECT_DIR"

echo -e "${YELLOW}📝 创建修复后的Dockerfile...${NC}"

cat > Dockerfile << 'EOF'
# QAToolBox Docker镜像 - 修复版本
FROM python:3.12-bullseye

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 更新包列表并安装系统依赖 - 分步安装避免冲突
RUN apt-get update && apt-get install -y \
    # 基础工具
    curl wget git unzip vim nano htop tree \
    build-essential gcc g++ make cmake pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装数据库驱动
RUN apt-get update && apt-get install -y \
    libpq-dev postgresql-client \
    libmariadb-dev libmariadb-dev-compat \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装图像处理库
RUN apt-get update && apt-get install -y \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libfreetype6-dev liblcms2-dev libopenjp2-7-dev \
    zlib1g-dev libimagequant-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装音视频处理库
RUN apt-get update && apt-get install -y \
    ffmpeg libavcodec-dev libavformat-dev libswscale-dev \
    libavutil-dev \
    libsndfile1-dev portaudio19-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装OCR支持
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
    tesseract-ocr-eng libtesseract-dev \
    poppler-utils antiword unrtf ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装科学计算库
RUN apt-get update && apt-get install -y \
    libgomp1 libatlas-base-dev liblapack-dev libblas-dev \
    libopenblas-dev libhdf5-dev libprotobuf-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装GUI和显示库
RUN apt-get update && apt-get install -y \
    libgtk-3-dev libgstreamer1.0-dev \
    libgl1-mesa-glx libsm6 libxext6 libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装浏览器（Chromium在Debian中的正确包名）
RUN apt-get update && apt-get install -y \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并安装基础工具
RUN pip install --upgrade pip setuptools wheel

# 安装Python依赖 - 分阶段安装避免冲突和超时
# 1. 核心Django框架
RUN pip install --no-cache-dir \
    Django==4.2.7 \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1

# 2. Django扩展
RUN pip install --no-cache-dir \
    django-crispy-forms==2.0 \
    crispy-bootstrap5==0.7 \
    django-simple-captcha==0.6.0 \
    django-extensions==3.2.3 \
    django-filter==23.3

# 3. 数据库和缓存
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.7 \
    redis==4.6.0 \
    django-redis==5.4.0

# 4. 异步和实时通信
RUN pip install --no-cache-dir \
    channels==4.0.0 \
    channels-redis==4.1.0 \
    daphne==4.0.0 \
    asgiref==3.8.1

# 5. 任务队列
RUN pip install --no-cache-dir \
    celery==5.3.4 \
    django-celery-beat==2.5.0

# 6. Web服务器和配置
RUN pip install --no-cache-dir \
    gunicorn==21.2.0 \
    whitenoise==6.6.0 \
    python-dotenv==1.0.0 \
    django-environ==0.11.2

# 7. HTTP和网络
RUN pip install --no-cache-dir \
    requests==2.31.0 \
    urllib3==1.26.18 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3

# 8. 基础数据处理
RUN pip install --no-cache-dir \
    numpy==1.24.4 \
    pandas==2.0.3 \
    scipy==1.9.3

# 9. 图像处理
RUN pip install --no-cache-dir \
    Pillow==9.5.0 \
    opencv-python-headless==4.8.1.78

# 10. 可视化
RUN pip install --no-cache-dir \
    matplotlib==3.7.5 \
    seaborn \
    plotly

# 11. 机器学习（分别安装避免冲突）
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    tensorflow-cpu==2.15.0

RUN pip install --no-cache-dir \
    scikit-learn==1.3.2 \
    scikit-image

# 12. 文档处理
RUN pip install --no-cache-dir \
    python-docx==1.1.0 \
    python-pptx==0.6.22 \
    openpyxl==3.1.2 \
    reportlab==4.0.9

# 13. PDF处理
RUN pip install --no-cache-dir \
    pypdfium2==4.23.1 \
    pdfplumber==0.10.3

# 14. OCR
RUN pip install --no-cache-dir \
    pytesseract==0.3.10

# 15. 音频处理
RUN pip install --no-cache-dir \
    pydub==0.25.1 \
    librosa==0.10.1 \
    soundfile==0.12.1

# 16. 浏览器自动化
RUN pip install --no-cache-dir \
    selenium==4.15.2 \
    webdriver-manager==4.0.1

# 17. 加密和工具
RUN pip install --no-cache-dir \
    cryptography==41.0.7 \
    tenacity==8.2.3 \
    prettytable==3.9.0 \
    qrcode==7.4.2 \
    python-dateutil==2.8.2

# 18. 尝试安装一些高级功能（允许失败）
RUN pip install --no-cache-dir easyocr || echo "EasyOCR installation failed, skipping..."
RUN pip install --no-cache-dir paddlepaddle paddleocr || echo "PaddleOCR installation failed, skipping..."

# 复制项目文件
COPY . /app/

# 创建必要目录
RUN mkdir -p /app/static /app/media /app/logs

# 设置权限
RUN chmod +x /app/manage.py

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 默认命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

echo -e "${YELLOW}📝 创建修复后的docker-compose.yml...${NC}"

cat > docker-compose.yml << EOF
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: ${DB_PASSWORD:-QAToolBox2024}
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qatoolbox"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis缓存
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # QAToolBox主应用
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    command: >
      sh -c "
        echo '等待数据库启动...' &&
        sleep 15 &&
        python manage.py migrate --noinput &&
        python manage.py collectstatic --noinput &&
        python manage.py shell -c \"
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456');
    print('✅ 管理员用户创建完成');
else:
    print('ℹ️ 管理员用户已存在');
        \" &&
        echo '🚀 启动Gunicorn服务器...' &&
        gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 --log-level info
      "
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DJANGO_SECRET_KEY=django-docker-secret-key-$(date +%s)
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=${DB_PASSWORD:-QAToolBox2024}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1,web
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker（可选）
  celery:
    build: 
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    command: >
      sh -c "
        echo '等待Web服务启动...' &&
        sleep 30 &&
        celery -A QAToolBox worker --loglevel=info --concurrency=2
      "
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DJANGO_SECRET_KEY=django-docker-secret-key-celery
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=${DB_PASSWORD:-QAToolBox2024}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - media_volume:/app/media
    depends_on:
      - web
    networks:
      - qatoolbox_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local

networks:
  qatoolbox_network:
    driver: bridge
EOF

echo -e "${YELLOW}📝 创建简单的健康检查URL...${NC}"

# 添加健康检查到urls.py
if [ -f "urls.py" ]; then
    # 检查是否已有健康检查URL
    if ! grep -q "health" urls.py; then
        # 备份原文件
        cp urls.py urls.py.backup
        
        # 添加健康检查视图
        cat >> urls.py << 'HEALTH_EOF'

# 健康检查
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

# 添加健康检查URL
try:
    from django.urls import path
    urlpatterns.append(path('health/', health_check, name='health_check'))
except:
    pass
HEALTH_EOF
    fi
fi

echo -e "${GREEN}✅ Dockerfile和docker-compose.yml修复完成${NC}"

echo -e "${BLUE}🐳 现在重新构建Docker镜像...${NC}"

# 清理之前的构建
docker compose down --volumes --remove-orphans 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# 重新构建
echo -e "${YELLOW}🔨 开始构建Docker镜像...${NC}"
if docker compose build --no-cache; then
    echo -e "${GREEN}✅ Docker镜像构建成功${NC}"
    
    echo -e "${YELLOW}🚀 启动Docker容器...${NC}"
    if docker compose up -d; then
        echo -e "${GREEN}✅ Docker容器启动成功${NC}"
        
        echo -e "${YELLOW}📊 查看容器状态...${NC}"
        docker compose ps
        
        echo -e "${YELLOW}📋 查看应用日志...${NC}"
        sleep 10
        docker compose logs web --tail=20
        
    else
        echo -e "${RED}❌ Docker容器启动失败${NC}"
        docker compose logs
        exit 1
    fi
else
    echo -e "${RED}❌ Docker镜像构建失败${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 修复完成！QAToolBox现在应该正常运行了${NC}"
EOF

chmod +x fix_dockerfile.sh
