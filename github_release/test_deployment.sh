#!/bin/bash
# QAToolBox 部署测试脚本
# =============================================
# 验证所有依赖和功能是否正常工作
# 服务器: 47.103.143.152
# 域名: https://shenyiqing.xin/
# =============================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 QAToolBox 部署测试开始...${NC}"

PROJECT_DIR="/home/qatoolbox/QAToolBox"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

# 测试函数
test_passed=0
test_failed=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}🔍 测试: $test_name${NC}"
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        ((test_passed++))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        ((test_failed++))
    fi
}

run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}🔍 测试: $test_name${NC}"
    
    if output=$(eval "$test_command" 2>&1); then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        echo "   输出: $output"
        ((test_passed++))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        echo "   错误: $output"
        ((test_failed++))
    fi
}

echo "=========================="
echo "🔧 系统服务测试"
echo "=========================="

# 测试系统服务
run_test "PostgreSQL 服务" "systemctl is-active postgresql"
run_test "Redis 服务" "systemctl is-active redis-server || systemctl is-active redis"
run_test "Nginx 服务" "systemctl is-active nginx"
run_test "Supervisor 服务" "systemctl is-active supervisor"

echo ""
echo "=========================="
echo "🐍 Python 环境测试"
echo "=========================="

# 测试Python环境
if [ -f "$PYTHON_BIN" ]; then
    echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    
    # 测试关键Python依赖
    run_test_with_output "Django" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import django; print(django.get_version())'"
    run_test_with_output "PyTorch" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import torch; print(torch.__version__)'"
    run_test_with_output "TorchVision" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import torchvision; print(torchvision.__version__)'"
    run_test_with_output "OpenCV" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import cv2; print(cv2.__version__)'"
    run_test_with_output "NumPy" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import numpy; print(numpy.__version__)'"
    run_test_with_output "Environ" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import environ; print(\"django-environ available\")'"
    run_test_with_output "Decouple" "cd $PROJECT_DIR && $PYTHON_BIN -c 'from decouple import config; print(\"python-decouple available\")'"
    run_test_with_output "Pillow" "cd $PROJECT_DIR && $PYTHON_BIN -c 'from PIL import Image; print(\"Pillow available\")'"
    run_test_with_output "Requests" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import requests; print(requests.__version__)'"
    run_test_with_output "Psycopg2" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import psycopg2; print(\"PostgreSQL driver available\")'"
    run_test_with_output "Redis Python" "cd $PROJECT_DIR && $PYTHON_BIN -c 'import redis; print(\"Redis Python client available\")'"
    
else
    echo -e "${RED}❌ 虚拟环境不存在: $PYTHON_BIN${NC}"
    ((test_failed++))
fi

echo ""
echo "=========================="
echo "🗄️ 数据库连接测试"
echo "=========================="

# 测试数据库连接
run_test "PostgreSQL 连接" "sudo -u postgres psql -c 'SELECT 1;'"
run_test "QAToolBox 数据库" "sudo -u postgres psql -d qatoolbox -c 'SELECT 1;'"
run_test "Redis 连接" "redis-cli ping"

echo ""
echo "=========================="
echo "🌐 网络服务测试"
echo "=========================="

# 测试端口监听
run_test "Nginx 端口 80" "netstat -tlnp | grep ':80 '"
run_test "PostgreSQL 端口 5432" "netstat -tlnp | grep ':5432 '"
run_test "Redis 端口 6379" "netstat -tlnp | grep ':6379 '"

# 测试HTTP访问
run_test "本地HTTP访问" "curl -s -o /dev/null -w '%{http_code}' http://localhost/ | grep -E '200|301|302'"
run_test "应用端口访问" "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/ | grep -E '200|301|302'"

echo ""
echo "=========================="
echo "📁 文件系统测试"
echo "=========================="

# 测试文件权限和目录
run_test "项目目录存在" "test -d $PROJECT_DIR"
run_test "环境文件存在" "test -f $PROJECT_DIR/.env"
run_test "静态文件目录" "test -d /var/www/qatoolbox/static || test -d $PROJECT_DIR/static"
run_test "媒体文件目录" "test -d /var/www/qatoolbox/media || test -d $PROJECT_DIR/media"
run_test "日志目录" "test -d $PROJECT_DIR/logs || test -d /var/log/"

echo ""
echo "=========================="
echo "🚀 Django 应用测试"
echo "=========================="

if [ -f "$PROJECT_DIR/manage.py" ]; then
    # 测试Django配置
    run_test "Django 配置检查" "cd $PROJECT_DIR && DJANGO_SETTINGS_MODULE=config.settings.production $PYTHON_BIN manage.py check --deploy"
    
    # 测试数据库迁移状态
    run_test "数据库迁移状态" "cd $PROJECT_DIR && DJANGO_SETTINGS_MODULE=config.settings.production $PYTHON_BIN manage.py showmigrations"
    
    # 测试静态文件收集
    run_test "静态文件检查" "cd $PROJECT_DIR && DJANGO_SETTINGS_MODULE=config.settings.production $PYTHON_BIN manage.py findstatic admin/css/base.css"
else
    echo -e "${RED}❌ manage.py 不存在${NC}"
    ((test_failed++))
fi

echo ""
echo "=========================="
echo "⚡ 进程管理测试"
echo "=========================="

# 测试Supervisor进程
run_test "QAToolBox 进程运行" "supervisorctl status qatoolbox | grep RUNNING"
run_test "进程重启测试" "supervisorctl restart qatoolbox && sleep 3 && supervisorctl status qatoolbox | grep RUNNING"

echo ""
echo "=========================="
echo "🎯 功能特性测试"
echo "=========================="

# 测试特定功能模块
if [ -f "$PROJECT_DIR/apps/tools/services/real_image_recognition.py" ]; then
    run_test "图像识别模块" "cd $PROJECT_DIR && $PYTHON_BIN -c 'from apps.tools.services.real_image_recognition import RealFoodImageRecognition; print(\"Image recognition module available\")'"
else
    echo -e "${YELLOW}⚠️  图像识别模块不存在${NC}"
fi

# 测试API端点（如果可用）
run_test "API 健康检查" "curl -s -f http://localhost/api/health/ >/dev/null || curl -s -f http://localhost/ >/dev/null"

echo ""
echo "=========================="
echo "📊 测试结果总结"
echo "=========================="

total_tests=$((test_passed + test_failed))
success_rate=$(( (test_passed * 100) / total_tests ))

echo -e "总测试数: ${BLUE}$total_tests${NC}"
echo -e "通过测试: ${GREEN}$test_passed${NC}"
echo -e "失败测试: ${RED}$test_failed${NC}"
echo -e "成功率: ${BLUE}$success_rate%${NC}"

if [ $test_failed -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 所有测试通过！部署成功！${NC}"
    echo ""
    echo "=========================="
    echo "🌐 访问信息"
    echo "=========================="
    echo -e "主站: ${BLUE}https://shenyiqing.xin/${NC}"
    echo -e "备用: ${BLUE}http://47.103.143.152/${NC}"
    echo -e "管理后台: ${BLUE}https://shenyiqing.xin/admin/${NC}"
    echo ""
    echo "管理员账号: admin / admin123456"
    echo ""
    echo "=========================="
    echo "🔧 常用管理命令"
    echo "=========================="
    echo "重启应用: supervisorctl restart qatoolbox"
    echo "查看日志: tail -f /var/log/qatoolbox.log"
    echo "重启Nginx: systemctl restart nginx"
    echo "检查状态: supervisorctl status"
    echo "=========================="
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ 有 $test_failed 个测试失败，请检查部署配置${NC}"
    echo ""
    echo "建议检查："
    echo "1. 依赖是否完全安装"
    echo "2. 服务是否正常启动"
    echo "3. 配置文件是否正确"
    echo "4. 权限设置是否正确"
    echo ""
    echo "查看日志："
    echo "- 应用日志: tail -f /var/log/qatoolbox.log"
    echo "- 错误日志: tail -f /var/log/qatoolbox_error.log"
    echo "- Nginx日志: tail -f /var/log/nginx/error.log"
    echo ""
    
    exit 1
fi
