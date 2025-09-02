# QAToolBox 公网部署指南

## 🚀 项目概述

QAToolBox 是一个基于Django的QA工具箱应用，支持公网访问。

**域名**: shenyiqing.com  
**端口**: 8000  
**技术栈**: Django 4.2+, Python 3.11+

## 📋 部署前准备

### 1. 系统要求
- macOS 10.15+
- Python 3.11+
- 网络连接（支持公网访问）

### 2. 域名配置
确保域名 `shenyiqing.com` 已正确解析到本机IP地址。

### 3. 网络配置
- 路由器端口转发：8000 → 8000
- 防火墙允许8000端口
- ISP不阻止8000端口

## 🔧 快速部署

### 方法1：使用部署脚本（推荐）

```bash
# 1. 给脚本执行权限
chmod +x deploy_public.sh

# 2. 运行部署脚本
./deploy_public.sh
```

### 方法2：手动部署

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements/base.txt

# 3. 运行数据库迁移
python manage.py migrate --settings=config.settings.production

# 4. 收集静态文件
python manage.py collectstatic --noinput --settings=config.settings.production

# 5. 启动服务
python start_public_server.py
```

## 🌐 访问地址

| 类型 | 地址 | 说明 |
|------|------|------|
| 本地访问 | http://localhost:8000 | 本机访问 |
| 内网访问 | http://[内网IP]:8000 | 局域网访问 |
| 公网访问 | http://shenyiqing.com:8000 | 互联网访问 |

## 🔍 健康检查

部署完成后，可以通过以下接口检查服务状态：

- **状态检查**: http://shenyiqing.com:8000/health/
- **连通性测试**: http://shenyiqing.com:8000/ping/
- **详细信息**: http://shenyiqing.com:8000/status/

## 🔒 安全配置

### 1. 防火墙配置

```bash
# 以管理员权限运行
sudo ./setup_firewall.sh
```

### 2. 安全头配置

已在 `config/settings/production.py` 中配置：
- XSS保护
- 内容类型嗅探保护
- HSTS安全头
- 点击劫持保护

### 3. 环境变量

复制并修改环境变量文件：

```bash
cp env.production .env
# 编辑 .env 文件，修改敏感信息
```

## 📊 监控和维护

### 1. 日志文件

- Django日志: `logs/django.log`
- 系统日志: 通过 `journalctl -u qatoolbox` 查看

### 2. 性能监控

通过健康检查接口监控：
- CPU使用率
- 内存使用情况
- 磁盘空间
- 数据库状态

### 3. 服务管理

```bash
# 启动服务
python start_public_server.py

# 后台运行
nohup python start_public_server.py > server.log 2>&1 &

# 停止服务
pkill -f "start_public_server.py"
```

## 🚨 故障排除

### 1. 端口被占用

```bash
# 检查端口占用
lsof -i :8000

# 杀死占用进程
kill -9 [PID]
```

### 2. 防火墙问题

```bash
# 检查防火墙状态
sudo pfctl -s rules

# 临时允许端口
sudo pfctl -f /etc/pf.conf
```

### 3. 域名解析问题

```bash
# 检查域名解析
nslookup shenyiqing.com
dig shenyiqing.com

# 检查本机IP
curl ifconfig.me
```

## 🔧 高级配置

### 1. Nginx反向代理

使用提供的 `nginx_config.conf` 配置Nginx：

```bash
# 安装Nginx
brew install nginx

# 复制配置文件
sudo cp nginx_config.conf /usr/local/etc/nginx/servers/qatoolbox.conf

# 重启Nginx
sudo nginx -s reload
```

### 2. SSL证书配置

建议使用Let's Encrypt免费SSL证书：

```bash
# 安装certbot
brew install certbot

# 获取证书
sudo certbot --nginx -d shenyiqing.com -d www.shenyiqing.com
```

### 3. 系统服务

将应用注册为系统服务：

```bash
# 复制服务文件
sudo cp qatoolbox.service /Library/LaunchDaemons/

# 启动服务
sudo launchctl load /Library/LaunchDaemons/qatoolbox.service
```

## 📞 技术支持

如遇到问题，请检查：

1. 日志文件中的错误信息
2. 网络连接和防火墙配置
3. 域名DNS解析状态
4. 服务进程状态

## 📝 更新日志

- **v1.0.0**: 初始部署版本
- 支持公网访问
- 健康检查接口
- 安全防护配置
- 自动化部署脚本
