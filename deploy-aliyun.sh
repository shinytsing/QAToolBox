#!/bin/bash

# QAToolBox 阿里云一键部署脚本
# 使用方法: ./deploy-aliyun.sh

set -e

echo "🚀 开始部署 QAToolBox 到阿里云..."

# 检查是否在阿里云服务器上
if [ ! -f /etc/aliyun-release ]; then
    echo "⚠️  警告: 此脚本建议在阿里云服务器上运行"
fi

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 安装 Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# 安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 安装 Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 安装Git
if ! command -v git &> /dev/null; then
    echo "📥 安装 Git..."
    sudo apt install git -y
fi

# 克隆项目
if [ ! -d "QAToolBox" ]; then
    echo "📥 克隆项目..."
    git clone https://github.com/shinytsing/QAToolBox.git QAToolBox
    cd QAToolBox
else
    echo "📥 更新项目..."
    cd QAToolBox
    git pull origin main
fi

# 配置环境变量
if [ ! -f .env ]; then
    echo "⚙️  配置环境变量..."
    cp .env.production .env
    echo "请编辑 .env 文件配置你的API密钥和密码"
    echo "按任意键继续..."
    read -n 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建新镜像
echo "🔨 构建新镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 运行数据库迁移
echo "📊 运行数据库迁移..."
docker-compose exec web python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec web python manage.py collectstatic --noinput

# 创建超级用户
echo "👤 创建超级用户..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

# 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw --force enable

# 检查健康状态
echo "🏥 检查健康状态..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ 部署成功！"
    echo "🌐 访问地址: http://47.103.143.152"
    echo "🌐 域名访问: http://shenyiqing.xin"
    echo "👤 管理员账号: admin / admin123"
else
    echo "❌ 健康检查失败，请检查日志"
    docker-compose logs web
    exit 1
fi

# 设置定时备份
echo "⏰ 设置定时备份..."
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && ./backup.sh") | crontab -

echo "🎉 部署完成！"
echo "📋 管理命令:"
echo "  - 查看状态: ./monitor.sh"
echo "  - 备份数据: ./backup.sh"
echo "  - 查看日志: docker-compose logs -f web"
echo "  - 重启服务: docker-compose restart"
