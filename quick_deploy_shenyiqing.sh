#!/bin/bash

# QAToolBox 沈一清快速部署脚本
# 一键部署到阿里云服务器 47.103.143.152

set -e

echo "🚀 开始部署QAToolBox到沈一清服务器..."
echo "服务器: 47.103.143.152"
echo "域名: shenyiqing.xin"
echo ""

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  建议不要使用root用户运行此脚本"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新系统
echo "📦 更新系统包..."
sudo apt-get update

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker安装完成"
else
    echo "✅ Docker已安装"
fi

# 安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 安装Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "✅ Docker Compose已安装"
fi

# 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable
echo "✅ 防火墙配置完成"

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p /opt/qatoolbox
sudo chown $USER:$USER /opt/qatoolbox
cd /opt/qatoolbox

# 克隆项目
if [[ -d "QAToolbox" ]]; then
    echo "📥 更新项目代码..."
    cd QAToolbox
    git pull origin main
else
    echo "📥 克隆项目代码..."
    git clone https://github.com/shinytsing/QAToolbox.git
    cd QAToolbox
fi

# 配置环境变量
if [[ ! -f ".env" ]]; then
    echo "⚙️  配置环境变量..."
    cp env.production .env
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    
    DB_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
    
    REDIS_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/redis123/$REDIS_PASSWORD/" .env
    
    echo "✅ 环境变量配置完成"
else
    echo "✅ 环境变量文件已存在"
fi

# 启动服务
echo "🚀 启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec web python manage.py migrate

# 创建超级用户
echo "👤 创建超级用户..."
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@shenyiqing.xin || true

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec web python manage.py collectstatic --noinput

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 检查应用健康状态..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health/ &>/dev/null; then
        echo "✅ 应用健康检查通过"
        break
    else
        echo "⏳ 等待应用启动... ($i/10)"
        sleep 10
    fi
done

echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152:8000"
echo "  - 域名地址: http://shenyiqing.xin:8000"
echo "  - 管理后台: http://47.103.143.152:8000/admin/"
echo ""
echo "👤 默认管理员账户:"
echo "  - 用户名: admin"
echo "  - 密码: 请通过以下命令设置:"
echo "    docker-compose exec web python manage.py changepassword admin"
echo ""
echo "🛠️  常用命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 更新代码: git pull && docker-compose up -d --build"
echo ""
echo "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
