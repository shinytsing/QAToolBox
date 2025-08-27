# QAToolBox 阿里云一键部署指南

🚀 **全新Ubuntu服务器，一键部署完整Django项目**

## 📋 快速开始

### 方式一：直接运行部署脚本

```bash
# 下载并执行一键部署脚本
wget -O deploy_aliyun.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun.sh
chmod +x deploy_aliyun.sh
sudo ./deploy_aliyun.sh
```

### 方式二：Git提交 + 自动部署

```bash
# 提交代码并自动部署到服务器
chmod +x git_deploy.sh
./git_deploy.sh -m "部署更新" -s YOUR_SERVER_IP

# 或者分步执行
./git_deploy.sh --commit-only -m "提交更新"
./git_deploy.sh --deploy-only -s YOUR_SERVER_IP
```

## 🌟 脚本特性

### ✨ 部署脚本特性（deploy_aliyun.sh）

- **🆕 全新服务器支持**: 支持Ubuntu 20.04/22.04/24.04
- **🔄 自动重试机制**: 网络问题自动重试，确保部署成功
- **🇨🇳 中国地区优化**: 阿里云镜像源，下载速度快
- **👤 管理员自动创建**: 初始管理员账户 admin/admin123456
- **📦 完整依赖安装**: 包含机器学习、数据处理、文档处理等所有功能
- **🔒 安全配置**: 防火墙、文件权限、服务安全配置
- **📊 详细日志**: 完整的部署日志记录
- **🎯 生产级配置**: Nginx + Gunicorn + PostgreSQL + Redis

### ✨ Git部署脚本特性（git_deploy.sh）

- **📝 智能提交**: 自动检测代码变更并提交
- **🚀 自动部署**: 代码提交后自动在服务器部署
- **🔑 SSH支持**: 支持密钥认证连接服务器
- **📋 灵活选项**: 支持仅提交、仅部署等模式
- **🔄 错误处理**: 完善的错误处理和重试机制

## 🛠️ 系统要求

### 服务器要求

- **操作系统**: Ubuntu 20.04/22.04/24.04 LTS
- **内存**: 建议 2GB 以上
- **磁盘空间**: 建议 20GB 以上
- **网络**: 需要公网IP和域名（可选）
- **权限**: 需要root权限

### 本地要求（使用Git部署脚本）

- **操作系统**: Linux/macOS/Windows WSL
- **依赖工具**: git, curl, ssh
- **权限**: 能够连接到目标服务器

## 📝 配置说明

### 环境变量配置

部署脚本会自动创建 `.env` 文件，主要配置项：

```bash
# Django基础配置
DJANGO_SECRET_KEY=自动生成的密钥
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

# 主机配置
ALLOWED_HOSTS=your-domain.com,your-server-ip

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=自动生成的密码

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

### 服务器配置

部署后的服务配置：

```bash
# 服务状态检查
sudo systemctl status nginx postgresql redis-server supervisor

# 应用状态检查
sudo supervisorctl status qatoolbox

# 查看应用日志
sudo tail -f /var/log/qatoolbox/gunicorn.log

# 重启应用
sudo supervisorctl restart qatoolbox
```

## 🎯 使用示例

### 示例1：全新服务器部署

```bash
# 在全新的Ubuntu服务器上执行
wget -O deploy_aliyun.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun.sh
chmod +x deploy_aliyun.sh
sudo ./deploy_aliyun.sh

# 预计15-25分钟完成部署
# 部署完成后访问 http://your-server-ip/
```

### 示例2：本地开发 + 远程部署

```bash
# 在本地项目目录下
chmod +x git_deploy.sh

# 提交代码并部署到阿里云服务器
./git_deploy.sh -m "添加新功能" -s 47.103.143.152

# 使用SSH密钥连接
./git_deploy.sh -s 47.103.143.152 -k ~/.ssh/aliyun_key

# 仅提交代码，不部署
./git_deploy.sh --commit-only -m "修复bug"

# 仅部署，不提交代码
./git_deploy.sh --deploy-only -s 47.103.143.152
```

### 示例3：自定义配置部署

```bash
# 设置环境变量后部署
export SERVER_IP="your-server-ip"
export DOMAIN="your-domain.com"
export DB_PASSWORD="your-db-password"
export ADMIN_PASSWORD="your-admin-password"

sudo ./deploy_aliyun.sh
```

## 📊 部署完成信息

部署成功后，您将看到类似信息：

```
========================================
🎉 QAToolBox 部署完成！
========================================

🌐 访问信息:
  主站地址: http://shenyiqing.xin/
  IP访问:   http://47.103.143.152/
  管理后台: http://shenyiqing.xin/admin/

👑 管理员账户:
  用户名: admin
  密码:   admin123456
  邮箱:   admin@shenyiqing.xin

📊 系统信息:
  项目目录: /home/qatoolbox/QAToolBox
  数据库:   PostgreSQL (qatoolbox)
  缓存:     Redis
  Python:   Python 3.x
  Django:   Django 4.2.7
```

## 🔧 故障排除

### 常见问题

1. **部署失败**
   ```bash
   # 查看详细日志
   sudo tail -f /tmp/qatoolbox_deploy_*.log
   
   # 检查服务状态
   sudo systemctl status nginx postgresql redis-server
   ```

2. **访问403/404错误**
   ```bash
   # 检查Nginx配置
   sudo nginx -t
   
   # 重启Nginx
   sudo systemctl restart nginx
   ```

3. **应用无法启动**
   ```bash
   # 查看应用日志
   sudo tail -f /var/log/qatoolbox/gunicorn.log
   
   # 重启应用
   sudo supervisorctl restart qatoolbox
   ```

4. **数据库连接失败**
   ```bash
   # 检查PostgreSQL状态
   sudo systemctl status postgresql
   
   # 检查数据库连接
   sudo -u postgres psql -c "SELECT 1;"
   ```

### 重新部署

如果需要重新部署：

```bash
# 清理旧部署
sudo supervisorctl stop qatoolbox
sudo rm -rf /home/qatoolbox/QAToolBox
sudo -u postgres dropdb qatoolbox 2>/dev/null || true

# 重新执行部署
sudo ./deploy_aliyun.sh
```

## 🔒 安全配置

### 防火墙设置

```bash
# 查看防火墙状态
sudo ufw status

# 开放新端口（如HTTPS）
sudo ufw allow 443/tcp

# 限制SSH访问（可选）
sudo ufw limit ssh
```

### SSL证书配置（可选）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 申请SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📋 维护命令

### 日常维护

```bash
# 查看系统状态
sudo supervisorctl status
sudo systemctl status nginx postgresql redis-server

# 查看应用日志
sudo tail -f /var/log/qatoolbox/gunicorn.log
sudo tail -f /var/log/qatoolbox/django.log

# 重启服务
sudo supervisorctl restart qatoolbox
sudo systemctl restart nginx

# 数据库备份
sudo -u postgres pg_dump qatoolbox > backup_$(date +%Y%m%d).sql

# 更新项目代码
cd /home/qatoolbox/QAToolBox
sudo -u qatoolbox git pull origin main
sudo supervisorctl restart qatoolbox
```

### 性能监控

```bash
# 查看系统资源
htop
df -h
free -h

# 查看网络连接
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# 查看日志大小
sudo du -sh /var/log/qatoolbox/
```

## 🆕 版本更新

### 手动更新

```bash
# 进入项目目录
cd /home/qatoolbox/QAToolBox

# 拉取最新代码
sudo -u qatoolbox git pull origin main

# 安装新依赖（如果有）
sudo -u qatoolbox .venv/bin/pip install -r requirements.txt

# 执行数据库迁移
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py migrate

# 收集静态文件
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py collectstatic --noinput

# 重启应用
sudo supervisorctl restart qatoolbox
```

### 自动更新（使用Git部署脚本）

```bash
# 本地提交更新并自动部署
./git_deploy.sh -m "版本更新" -s your-server-ip
```

## 📞 技术支持

如果遇到问题：

1. **查看日志**: `/tmp/qatoolbox_deploy_*.log`
2. **检查文档**: 参考本文档的故障排除部分
3. **社区支持**: 提交Issue到GitHub仓库
4. **在线文档**: https://github.com/shinytsing/QAToolbox

---

**🎉 现在开始享受您的QAToolBox吧！**
