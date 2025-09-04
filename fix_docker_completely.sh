#!/bin/bash

# 完全修复Docker镜像问题

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "完全修复Docker镜像问题"
log_info "=========================================="

# 1. 完全停止Docker服务
log_info "停止Docker服务..."
systemctl stop docker
sleep 5

# 2. 清理Docker配置
log_info "清理Docker配置..."
rm -f /etc/docker/daemon.json
rm -rf /var/lib/docker/tmp/*

# 3. 配置新的Docker镜像加速器
log_info "配置新的Docker镜像加速器..."
mkdir -p /etc/docker

cat > /etc/docker/daemon.json << 'EOF'
{
    "registry-mirrors": [
        "https://registry.cn-hangzhou.aliyuncs.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ],
    "insecure-registries": [],
    "debug": false,
    "experimental": false,
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
EOF

# 4. 重启Docker服务
log_info "重启Docker服务..."
systemctl daemon-reload
systemctl start docker
sleep 20

# 5. 验证Docker配置
log_info "验证Docker配置..."
docker info | grep -A 10 "Registry Mirrors"

# 6. 测试镜像拉取
log_info "测试镜像拉取..."
if docker pull python:3.12-slim; then
    log_success "镜像拉取成功"
else
    log_warning "镜像拉取失败，尝试手动拉取..."
    
    # 尝试从阿里云直接拉取
    if docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.12-slim; then
        log_info "从阿里云拉取成功，重新标记镜像..."
        docker tag registry.cn-hangzhou.aliyuncs.com/library/python:3.12-slim python:3.12-slim
        log_success "镜像重新标记成功"
    else
        log_error "所有镜像源都失败"
        exit 1
    fi
fi

# 7. 进入项目目录
log_info "进入项目目录..."
cd /home/admin/QAToolbox

# 8. 配置环境变量
log_info "配置环境变量..."
if [[ ! -f ".env" ]]; then
    cp env.production .env
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    
    DB_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
    
    REDIS_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/redis123/$REDIS_PASSWORD/" .env
    
    # 更新允许的主机
    sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin/" .env
fi

log_success "环境变量配置完成"

# 9. 启动Docker服务
log_info "启动Docker服务..."

# 停止现有服务
docker compose down 2>/dev/null || true

# 清理旧的镜像和容器
docker system prune -f

# 构建镜像
log_info "构建Docker镜像..."
docker compose build --no-cache

# 启动服务
log_info "启动Docker服务..."
docker compose up -d

# 等待服务启动
log_info "等待服务启动..."
sleep 60

log_success "Docker服务启动完成"

# 10. 数据库迁移和初始化
log_info "数据库迁移和初始化..."

# 等待数据库服务完全启动
log_info "等待数据库服务启动..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U qatoolbox -d qatoolbox_production &>/dev/null; then
        log_info "数据库服务已就绪"
        break
    else
        log_info "等待数据库启动... ($i/30)"
        sleep 10
    fi
done

# 运行数据库迁移
log_info "运行数据库迁移..."
docker compose exec -T web python manage.py migrate

# 创建超级用户
log_info "创建超级用户..."
docker compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"

# 收集静态文件
log_info "收集静态文件..."
docker compose exec -T web python manage.py collectstatic --noinput

log_success "数据库初始化完成"

# 11. 健康检查
log_info "健康检查..."

# 检查容器状态
log_info "检查容器状态..."
docker compose ps

# 检查应用健康状态
log_info "检查应用健康状态..."
for i in {1..20}; do
    if curl -f http://localhost:8000/health/ &>/dev/null; then
        log_success "应用健康检查通过"
        break
    else
        log_info "等待应用启动... ($i/20)"
        sleep 15
    fi
done

log_success "健康检查完成"

# 12. 显示部署结果
log_success "=========================================="
log_success "🎉 QAToolBox 部署完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152:8000"
echo "  - 域名地址: http://shenyiqing.xin:8000"
echo "  - 管理后台: http://47.103.143.152:8000/admin/"
echo "  - 健康检查: http://47.103.143.152:8000/health/"
echo
log_info "👤 管理员账户:"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo "  - 邮箱: admin@shenyiqing.xin"
echo
log_info "🛠️  常用管理命令:"
echo "  - 查看服务状态: docker compose ps"
echo "  - 查看日志: docker compose logs -f"
echo "  - 重启服务: docker compose restart"
echo "  - 停止服务: docker compose down"
echo "  - 进入容器: docker compose exec web bash"
echo
log_success "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
log_success "=========================================="
