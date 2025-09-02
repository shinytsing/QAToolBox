#!/bin/bash
# macOS防火墙配置脚本
# 允许Django服务通过防火墙

echo "🔒 配置macOS防火墙..."

# 检查是否以管理员权限运行
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  请以管理员权限运行此脚本: sudo ./setup_firewall.sh"
    exit 1
fi

# 获取本机IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
echo "📍 本机IP: $LOCAL_IP"

# 配置防火墙规则
echo "🔧 添加防火墙规则..."

# 允许8000端口入站连接
/usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
/usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3

# 配置pf防火墙规则（如果启用）
if [ -f /etc/pf.conf ]; then
    echo "📝 配置pf防火墙..."
    
    # 备份原配置
    cp /etc/pf.conf /etc/pf.conf.backup
    
    # 添加Django服务规则
    cat >> /etc/pf.conf << EOF

# Django服务规则
pass in proto tcp from any to $LOCAL_IP port 8000
pass out proto tcp from $LOCAL_IP to any port 8000
EOF
    
    # 重新加载pf配置
    pfctl -f /etc/pf.conf
    echo "✅ pf防火墙配置已更新"
fi

# 检查端口是否开放
echo "🔍 检查端口状态..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ 端口8000已开放"
else
    echo "⚠️  端口8000未开放，请检查服务是否启动"
fi

echo "🎉 防火墙配置完成！"
echo "📋 注意事项:"
echo "   1. 确保路由器端口转发配置正确"
echo "   2. 检查ISP是否阻止了8000端口"
echo "   3. 考虑使用标准端口(80/443)避免被阻止"
