#!/bin/bash
# QAToolBox 公网部署脚本
# 支持从网络配置、安全防护、服务稳定性三个维度配置

set -e

echo "🚀 QAToolBox 公网部署开始..."
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 检查Python环境
check_python() {
    echo -e "${BLUE}🔍 检查Python环境...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"
    
    # 检查虚拟环境
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
    else
        echo -e "${YELLOW}⚠️  建议在虚拟环境中运行${NC}"
    fi
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}📦 安装项目依赖...${NC}"
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    elif [ -f "requirements/base.txt" ]; then
        pip3 install -r requirements/base.txt
    else
        echo -e "${YELLOW}⚠️  未找到requirements文件，尝试安装基础依赖${NC}"
        pip3 install django djangorestframework django-cors-headers psutil
    fi
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 数据库迁移
run_migrations() {
    echo -e "${BLUE}🗄️  运行数据库迁移...${NC}"
    
    python3 manage.py makemigrations --settings=config.settings.production
    python3 manage.py migrate --settings=config.settings.production
    
    echo -e "${GREEN}✅ 数据库迁移完成${NC}"
}

# 收集静态文件
collect_static() {
    echo -e "${BLUE}📁 收集静态文件...${NC}"
    
    python3 manage.py collectstatic --noinput --settings=config.settings.production
    
    echo -e "${GREEN}✅ 静态文件收集完成${NC}"
}

# 创建超级用户
create_superuser() {
    echo -e "${BLUE}👤 检查超级用户...${NC}"
    
    if ! python3 manage.py shell --settings=config.settings.production -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('需要创建超级用户')
    exit(1)
else:
    print('超级用户已存在')
    exit(0)
" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  未找到超级用户，请手动创建：${NC}"
        echo "python3 manage.py createsuperuser --settings=config.settings.production"
    else
        echo -e "${GREEN}✅ 超级用户已存在${NC}"
    fi
}

# 配置防火墙
setup_firewall() {
    echo -e "${BLUE}🔒 配置防火墙...${NC}"
    
    if [ -f "setup_firewall.sh" ]; then
        chmod +x setup_firewall.sh
        echo -e "${YELLOW}⚠️  请以管理员权限运行防火墙配置：${NC}"
        echo "sudo ./setup_firewall.sh"
    else
        echo -e "${YELLOW}⚠️  防火墙配置脚本不存在${NC}"
    fi
}

# 启动服务
start_service() {
    echo -e "${BLUE}🚀 启动Django服务...${NC}"
    
    if [ -f "start_public_server.py" ]; then
        echo -e "${GREEN}✅ 使用公网启动脚本${NC}"
        python3 start_public_server.py
    else
        echo -e "${YELLOW}⚠️  使用标准Django启动${NC}"
        python3 manage.py runserver 0.0.0.0:8000 --settings=config.settings.production --noreload
    fi
}

# 显示部署信息
show_deployment_info() {
    echo -e "${BLUE}📋 部署信息${NC}"
    echo "=================================="
    echo -e "${GREEN}项目名称:${NC} QAToolBox"
    echo -e "${GREEN}项目路径:${NC} $PROJECT_ROOT"
    echo -e "${GREEN}域名:${NC} shenyiqing.com"
    echo -e "${GREEN}端口:${NC} 8000"
    echo -e "${GREEN}配置文件:${NC} config/settings/production.py"
    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo "  本地: http://localhost:8000"
    echo "  内网: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  公网: http://shenyiqing.com:8000"
    echo ""
    echo -e "${BLUE}健康检查:${NC}"
    echo "  状态: http://shenyiqing.com:8000/health/"
    echo "  Ping: http://shenyiqing.com:8000/ping/"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo "  1. 确保域名DNS解析到本机IP"
    echo "  2. 配置路由器端口转发 (8000 -> 8000)"
    echo "  3. 检查防火墙是否允许8000端口"
    echo "  4. 考虑使用Nginx反向代理"
}

# 主函数
main() {
    echo -e "${GREEN}开始部署流程...${NC}"
    
    check_python
    install_dependencies
    run_migrations
    collect_static
    create_superuser
    setup_firewall
    
    echo -e "${GREEN}🎉 部署准备完成！${NC}"
    echo ""
    
    show_deployment_info
    
    echo ""
    echo -e "${BLUE}是否现在启动服务？(y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        start_service
    else
        echo -e "${GREEN}部署完成！请手动启动服务：${NC}"
        echo "python3 start_public_server.py"
        echo "或"
        echo "python3 manage.py runserver 0.0.0.0:8000 --settings=config.settings.production"
    fi
}

# 错误处理
trap 'echo -e "${RED}❌ 部署过程中出现错误${NC}"; exit 1' ERR

# 运行主函数
main "$@"
