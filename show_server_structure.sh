#!/bin/bash
# =============================================================================
# 阿里云服务器文件结构展示脚本
# 用于分析服务器上的实际文件结构和配置
# =============================================================================

echo "🔍 开始分析阿里云服务器文件结构..."

# 1. 显示项目根目录结构
echo "=== 项目根目录结构 ==="
ls -la /home/qatoolbox/QAToolBox/

echo ""
echo "=== 项目子目录结构 ==="
ls -la /home/qatoolbox/QAToolBox/apps/
ls -la /home/qatoolbox/QAToolBox/config/
ls -la /home/qatoolbox/QAToolBox/templates/
ls -la /home/qatoolbox/QAToolBox/static/

echo ""
echo "=== 用户应用结构 ==="
ls -la /home/qatoolbox/QAToolBox/apps/users/
ls -la /home/qatoolbox/QAToolBox/apps/tools/
ls -la /home/qatoolbox/QAToolBox/apps/content/

echo ""
echo "=== 配置文件 ==="
ls -la /home/qatoolbox/QAToolBox/config/settings/
ls -la /home/qatoolbox/QAToolBox/*.py | head -10

echo ""
echo "=== Nginx配置 ==="
echo "--- 主配置文件 ---"
cat /etc/nginx/nginx.conf

echo ""
echo "--- 站点配置 ---"
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/

echo ""
echo "--- QAToolBox站点配置 ---"
if [ -f "/etc/nginx/sites-available/qatoolbox" ]; then
    cat /etc/nginx/sites-available/qatoolbox
else
    echo "QAToolBox站点配置文件不存在"
fi

echo ""
echo "=== 服务状态 ==="
systemctl status nginx --no-pager
systemctl status postgresql --no-pager
systemctl status redis-server --no-pager
supervisorctl status qatoolbox

echo ""
echo "=== 日志文件 ==="
ls -la /var/log/qatoolbox/
ls -la /var/log/nginx/

echo ""
echo "=== 环境变量 ==="
if [ -f "/home/qatoolbox/QAToolBox/.env" ]; then
    echo "--- .env文件内容 ---"
    cat /home/qatoolbox/QAToolBox/.env
else
    echo ".env文件不存在"
fi

echo ""
echo "=== Python环境 ==="
ls -la /home/qatoolbox/QAToolBox/.venv/
which python3
python3 --version

echo ""
echo "=== 数据库状态 ==="
sudo -u postgres psql -c "\l" 2>/dev/null || echo "PostgreSQL连接失败"

echo ""
echo "=== 网络连接 ==="
netstat -tlnp | grep -E ':(80|443|5432|6379|8000)\s'

echo ""
echo "=== 磁盘使用 ==="
df -h

echo ""
echo "=== 内存使用 ==="
free -h

echo ""
echo "=== 最近的错误日志 ==="
echo "--- Gunicorn错误日志 ---"
tail -20 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || echo "无Gunicorn错误日志"

echo ""
echo "--- Nginx错误日志 ---"
tail -20 /var/log/nginx/error.log 2>/dev/null || echo "无Nginx错误日志"

echo ""
echo "=== 应用日志 ---"
tail -20 /var/log/qatoolbox/gunicorn.log 2>/dev/null || echo "无应用日志"

echo ""
echo "🔍 服务器结构分析完成！"
echo "请将以上输出内容发送给我，我会根据实际情况创建针对性的修复脚本。"
