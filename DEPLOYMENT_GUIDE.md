# QAToolBox 一键部署指南

## 🚀 快速部署

### 服务器信息
- **服务器IP**: 47.103.143.152
- **域名**: https://shenyiqing.xin/
- **系统**: Ubuntu/CentOS Linux

### 一键部署命令

```bash
# 方法1: 完整部署（推荐）
sudo bash deploy_complete_with_all_deps.sh

# 方法2: 快速部署
sudo bash deploy_quick_start.sh
```

## 📋 部署步骤详解

### 1. 环境隔离 (Virtual Environment)
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate
```

### 2. 依赖安装
```bash
# 使用完整依赖文件（包含torch、environ等）
pip install -r requirements_complete.txt

# 或使用基础依赖文件
pip install -r requirements.txt
```

### 3. 系统级依赖安装
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-dev build-essential \
    libpq-dev libffi-dev libssl-dev \
    libjpeg-dev libpng-dev zlib1g-dev \
    postgresql redis-server nginx

# CentOS/RHEL
sudo yum install -y \
    python3-devel gcc gcc-c++ \
    postgresql-devel openssl-devel \
    libjpeg-devel libpng-devel zlib-devel \
    postgresql-server redis nginx
```

### 4. 数据库配置
```bash
# PostgreSQL
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
```

### 5. 环境变量配置
```bash
# 复制环境配置文件
cp env.production.complete .env

# 或手动配置关键变量
cat > .env << 'EOF'
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
REDIS_URL=redis://localhost:6379/0
EOF
```

## 🔧 解决的依赖问题

### 机器学习依赖
- ✅ **torch**: 深度学习框架
- ✅ **torchvision**: 计算机视觉
- ✅ **opencv-python**: 图像处理
- ✅ **scikit-learn**: 机器学习
- ✅ **numpy**: 数值计算

### 环境变量管理
- ✅ **django-environ**: Django环境变量
- ✅ **python-decouple**: 配置管理
- ✅ **python-dotenv**: .env文件支持

### 系统级依赖
- ✅ **PostgreSQL**: 数据库
- ✅ **Redis**: 缓存和任务队列
- ✅ **Nginx**: Web服务器
- ✅ **Supervisor**: 进程管理

## 📁 部署文件说明

### 依赖文件
- `requirements_complete.txt`: 完整依赖列表（包含所有功能）
- `requirements.txt`: 基础依赖列表
- `requirements_production.txt`: 生产环境依赖

### 配置文件
- `env.production.complete`: 完整生产环境配置
- `.env.example`: 环境变量示例
- `config/settings/production.py`: Django生产配置

### 部署脚本
- `deploy_complete_with_all_deps.sh`: 完整一键部署脚本
- `deploy_quick_start.sh`: 快速部署脚本

## 🧪 验证部署

### 检查服务状态
```bash
# 检查系统服务
systemctl status nginx postgresql redis-server supervisor

# 检查应用进程
supervisorctl status qatoolbox

# 检查端口监听
netstat -tlnp | grep -E ":(80|443|8000|5432|6379)"
```

### 测试功能
```bash
# 测试网站访问
curl -I http://localhost/
curl -I http://47.103.143.152/

# 测试依赖导入
cd /home/qatoolbox/QAToolBox
.venv/bin/python -c "import torch; print('torch version:', torch.__version__)"
.venv/bin/python -c "import cv2; print('opencv version:', cv2.__version__)"
.venv/bin/python -c "import environ; print('environ imported successfully')"
```

## 🔍 故障排除

### 常见问题

#### 1. torch 导入失败
```bash
# 解决方案
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 2. environ 模块缺失
```bash
# 解决方案
pip install django-environ python-decouple
```

#### 3. OpenCV 导入失败
```bash
# 解决方案
apt install -y libgl1-mesa-glx libglib2.0-0
pip install opencv-python opencv-contrib-python
```

#### 4. PostgreSQL 连接失败
```bash
# 检查服务状态
systemctl status postgresql

# 重置密码
sudo -u postgres psql -c "ALTER USER qatoolbox PASSWORD 'QAToolBox@2024';"
```

### 日志查看
```bash
# 应用日志
tail -f /var/log/qatoolbox.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Django日志
tail -f /home/qatoolbox/QAToolBox/logs/django.log
```

## 🎯 部署后访问

### 网站访问
- 主站: https://shenyiqing.xin/
- 备用: http://47.103.143.152/
- 管理后台: https://shenyiqing.xin/admin/

### 默认管理员账号
- 用户名: admin
- 密码: admin123456

### 管理命令
```bash
# 重启应用
supervisorctl restart qatoolbox

# 重启Nginx
systemctl restart nginx

# 查看进程状态
supervisorctl status

# 更新代码后重启
cd /home/qatoolbox/QAToolBox
git pull
supervisorctl restart qatoolbox
```

## 📞 技术支持

如果遇到部署问题，请检查：
1. 系统版本兼容性
2. 网络连接状况
3. 权限设置
4. 日志文件错误信息

---

**注意**: 部署过程中会自动安装所有必需依赖，包括torch、environ等，确保功能完整性。
