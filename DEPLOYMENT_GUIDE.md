# QAToolBox 部署指南

## 📋 概述

QAToolBox 支持多种部署方式，包括传统服务器部署和容器化部署。

## 🚀 快速开始

### 1. 传统服务器部署

#### 使用优化部署脚本

```bash
# 生产环境部署
./deploy.sh -e production -s 47.103.143.152

# 开发环境部署
./deploy.sh -e development -s localhost -u root

# 查看帮助
./deploy.sh --help
```

#### 手动部署步骤

1. **安装系统依赖**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev git nginx redis-server
```

2. **克隆项目**
```bash
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox
```

3. **设置Python环境**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/prod.txt  # 生产环境
# 或
pip install -r requirements/dev.txt   # 开发环境
```

4. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. **数据库迁移**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

6. **启动服务**
```bash
# 生产环境
gunicorn --bind 127.0.0.1:8000 --workers 4 config.wsgi:application

# 开发环境
python manage.py runserver 0.0.0.0:8000
```

### 2. Docker 容器化部署

#### 使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 单独使用 Docker

```bash
# 构建镜像
docker build -t qatoolbox .

# 运行容器
docker run -d -p 8000:8000 --name qatoolbox qatoolbox
```

## 📦 依赖管理

### 分层依赖结构

```
requirements/
├── base.txt          # 基础依赖（所有环境都需要）
├── dev.txt           # 开发环境依赖（-r base.txt）
├── prod.txt          # 生产环境依赖（-r base.txt）
└── requirements.txt  # 兼容性文件（-r base.txt）
```

### 安装方式

```bash
# 开发环境
pip install -r requirements/dev.txt

# 生产环境
pip install -r requirements/prod.txt

# 仅基础依赖
pip install -r requirements/base.txt
```

### 主要依赖说明

#### 核心框架
- **Django 4.2.23**: Web框架
- **DRF 3.16.0**: REST API框架
- **django-cors-headers**: 跨域支持
- **django-crispy-forms**: 表单美化

#### 数据处理
- **pandas 2.3.1**: 数据分析
- **numpy 2.0.2**: 数值计算
- **matplotlib 3.9.4**: 数据可视化
- **pyecharts 2.0.8**: 图表库

#### 文件处理
- **Pillow 11.3.0**: 图像处理
- **python-docx 1.2.0**: Word文档
- **pdfplumber 0.11.7**: PDF处理
- **xmind 1.2.0**: 思维导图

#### 网络请求
- **requests 2.32.4**: HTTP客户端
- **beautifulsoup4 4.13.4**: HTML解析
- **lxml 6.0.0**: XML处理

#### 异步任务
- **celery 5.5.3**: 任务队列
- **redis 6.2.0**: 缓存和消息代理

## 🔧 配置说明

### 环境变量

```bash
# 必需的环境变量
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 数据库配置
DATABASE_URL=postgres://user:password@host:port/dbname
# 或
DB_ENGINE=django.db.backends.postgresql
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 数据库配置

#### PostgreSQL（推荐）
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### SQLite（开发环境）
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🚀 性能优化

### 1. 缓存配置

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. 静态文件

```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 使用CDN或Nginx服务静态文件
```

### 3. 数据库优化

```python
# 数据库连接池
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}
```

## 🔒 安全配置

### 1. 生产环境安全设置

```python
# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS设置
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### 2. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📊 监控和日志

### 1. 日志配置

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. 健康检查

```python
# 在 urls.py 中添加健康检查端点
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("healthy", content_type="text/plain")

urlpatterns = [
    # ... 其他URL
    path('health/', health_check, name='health_check'),
]
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接参数
   - 确认防火墙设置

2. **静态文件404**
   - 运行 `python manage.py collectstatic`
   - 检查Nginx配置
   - 验证文件权限

3. **Celery任务失败**
   - 检查Redis连接
   - 验证Celery配置
   - 查看Celery日志

4. **内存不足**
   - 减少Gunicorn worker数量
   - 优化数据库查询
   - 增加服务器内存

### 日志查看

```bash
# Django日志
tail -f /var/log/qatoolbox/django.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Gunicorn日志
tail -f gunicorn.log

# Celery日志
tail -f celery.log
```

## 📞 支持

如果遇到部署问题，请：

1. 查看相关日志文件
2. 检查环境变量配置
3. 验证依赖版本兼容性
4. 提交Issue到GitHub仓库

## 📝 更新日志

- **v1.0.0**: 初始版本
- **v1.1.0**: 添加Docker支持
- **v1.2.0**: 优化依赖管理
- **v1.3.0**: 添加部署脚本 