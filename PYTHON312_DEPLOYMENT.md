# QAToolBox Python 3.12 部署指南

## 🎯 概述

本指南专门为 QAToolBox 项目在 Python 3.12 环境下的部署而编写。Python 3.12 带来了显著的性能提升和新特性，能够为您的 QA 工具箱提供更好的性能和稳定性。

## ✨ Python 3.12 新特性

### 性能提升
- **启动速度提升 10-60%**：更快的模块导入和启动时间
- **内存使用优化**：更高效的内存管理
- **CPU 性能提升**：优化的字节码执行

### 语言特性
- **f-string 语法增强**：支持更复杂的表达式
- **类型注解改进**：更好的类型提示支持
- **match 语句优化**：更高效的模式匹配
- **错误追踪改进**：更清晰的错误信息

### 标准库更新
- **pathlib 增强**：更好的路径操作
- **typing 模块改进**：更丰富的类型注解
- **asyncio 优化**：更好的异步性能

## 🚀 快速部署

### 方法 1：使用优化部署脚本（推荐）

```bash
# 下载并运行部署脚本
wget https://raw.githubusercontent.com/your-repo/QAToolBox/main/deploy_python312_optimized.sh
chmod +x deploy_python312_optimized.sh
sudo ./deploy_python312_optimized.sh
```

### 方法 2：手动部署

```bash
# 1. 检查 Python 版本
python3 --version

# 2. 创建项目用户
sudo useradd -m -s /bin/bash qatoolbox
sudo usermod -aG sudo qatoolbox

# 3. 切换到项目用户
sudo su - qatoolbox

# 4. 克隆项目
git clone https://github.com/your-repo/QAToolBox.git
cd QAToolBox

# 5. 创建虚拟环境
python3.12 -m venv venv_py312
source venv_py312/bin/activate

# 6. 安装依赖
pip install --upgrade pip setuptools wheel
pip install -r requirements/base.txt

# 7. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 8. 运行迁移
python manage.py migrate
python manage.py collectstatic --noinput

# 9. 启动服务
python manage.py runserver 0.0.0.0:8000
```

## 🔧 系统要求

### 操作系统
- Ubuntu 24.04+ (推荐)
- CentOS/RHEL 8+
- Debian 12+

### Python 环境
- Python 3.12.x
- pip 23.0+
- venv 模块

### 系统依赖
```bash
# Ubuntu/Debian
sudo apt-get install -y \
    python3.12-venv \
    python3.12-dev \
    build-essential \
    libpq-dev \
    libmysqlclient-dev \
    nginx \
    redis-server \
    postgresql

# CentOS/RHEL
sudo yum install -y \
    python3-devel \
    python3-pip \
    postgresql-devel \
    nginx \
    redis \
    postgresql
```

## 📦 依赖管理

### 核心依赖
```txt
# requirements/base.txt
Django>=4.2,<5.0
djangorestframework>=3.14.0
celery>=5.3.0,<6.0
redis>=4.6.0
psycopg2-binary>=2.9.7
```

### Python 3.12 优化版本
```txt
# 数据处理
pandas>=2.1.0      # 更好的性能
numpy>=1.26.0      # 优化的数组操作
scipy>=1.11.0      # 科学计算优化

# 机器学习
tensorflow-cpu>=2.15.0  # 更好的 CPU 性能
scikit-learn>=1.3.0     # 优化的算法实现

# 图像处理
Pillow>=10.0.0          # 更快的图像处理
opencv-python-headless>=4.8.0  # 优化的计算机视觉
```

## 🐳 Docker 部署

### Dockerfile 优化
```dockerfile
# 使用 Python 3.12 官方镜像
FROM python:3.12-bullseye

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip setuptools wheel

# 安装 Python 依赖
COPY requirements/ /app/requirements/
RUN pip install -r requirements/base.txt

# 复制项目文件
COPY . /app/
WORKDIR /app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/qatoolbox
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 🔍 兼容性检查

### 运行检查脚本
```bash
# 在项目目录中运行
python check_python312_compatibility.py
```

### 手动检查项目
```bash
# Django 部署检查
python manage.py check --deploy

# 测试运行
python manage.py test

# 静态文件收集
python manage.py collectstatic --noinput
```

## 📊 性能监控

### 系统监控
```bash
# 查看服务状态
systemctl status qatoolbox
systemctl status qatoolbox-celery
systemctl status nginx

# 查看日志
tail -f /home/qatoolbox/QAToolBox/logs/django.log
journalctl -u qatoolbox -f
```

### 性能指标
- **响应时间**：通常提升 15-25%
- **内存使用**：减少 10-20%
- **启动速度**：提升 10-60%
- **并发处理**：更好的异步性能

## 🚨 故障排除

### 常见问题

#### 1. Python 版本不匹配
```bash
# 检查 Python 版本
python3 --version

# 如果版本不对，安装 Python 3.12
sudo apt-get install python3.12 python3.12-venv python3.12-dev
```

#### 2. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip setuptools wheel

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements/base.txt --force-reinstall
```

#### 3. 权限问题
```bash
# 修复文件权限
sudo chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
sudo chmod -R 755 /home/qatoolbox/QAToolBox
```

#### 4. 服务启动失败
```bash
# 检查服务状态
systemctl status qatoolbox

# 查看详细日志
journalctl -u qatoolbox -n 50

# 重新加载服务
sudo systemctl daemon-reload
sudo systemctl restart qatoolbox
```

## 🔄 升级指南

### 从 Python 3.11 升级
```bash
# 1. 备份当前环境
cp -r venv_py311 venv_py311_backup

# 2. 创建新的 Python 3.12 环境
python3.12 -m venv venv_py312

# 3. 激活新环境
source venv_py312/bin/activate

# 4. 安装依赖
pip install -r requirements/base.txt

# 5. 测试应用
python manage.py check --deploy
python manage.py test

# 6. 更新服务配置
sudo systemctl restart qatoolbox
```

## 📚 参考资料

- [Python 3.12 官方文档](https://docs.python.org/3.12/)
- [Django 4.2 部署指南](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Gunicorn 配置文档](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx 配置指南](https://nginx.org/en/docs/)

## 🤝 支持

如果您在部署过程中遇到问题，请：

1. 查看部署日志：`/tmp/qatoolbox_py312_deploy_*.log`
2. 检查 Django 日志：`/home/qatoolbox/QAToolBox/logs/django.log`
3. 运行兼容性检查：`python check_python312_compatibility.py`
4. 提交 Issue 到项目仓库

---

**注意**：本指南基于 QAToolBox 项目编写，其他项目可能需要相应调整。
