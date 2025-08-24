# 🚀 QAToolBox 阿里云部署指南

## 📋 部署概述

本指南将帮助您在阿里云 CentOS 服务器上一键部署 QAToolBox 项目，支持 HTTPS 访问和生产环境配置。

## 🖥️ 系统要求

### 服务器配置
- **操作系统**: CentOS 7/8/9, RHEL 7/8/9, Rocky Linux, AlmaLinux
- **内存**: 最低 2GB，推荐 4GB 或更高
- **存储**: 最低 20GB，推荐 40GB 或更高
- **网络**: 公网IP，开放 80 和 443 端口

### 阿里云实例推荐
- **规格**: ecs.c6.large (2核4GB) 或更高
- **镜像**: CentOS 8.4 64位 或 CentOS 7.9 64位
- **磁盘**: 系统盘 40GB + 数据盘 50GB（可选）
- **网络**: 专有网络 VPC

## 🔧 预配置步骤

### 1. 创建阿里云ECS实例
1. 登录阿里云控制台
2. 创建ECS实例，选择CentOS系统
3. 配置安全组，开放以下端口：
   - 22 (SSH)
   - 80 (HTTP)
   - 443 (HTTPS)
   - 8000 (Django开发端口，可选)

### 2. 连接服务器
```bash
# 使用SSH连接服务器
ssh root@YOUR_SERVER_IP

# 或使用阿里云控制台的远程连接功能
```

### 3. 系统初始化（可选但推荐）
```bash
# 更新系统
yum update -y

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 创建swap（如果内存小于4GB）
dd if=/dev/zero of=/swapfile bs=1024 count=2097152
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
```

## 🚀 一键部署

### 方法一：直接下载部署脚本
```bash
# 下载部署脚本
curl -O https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_centos.sh

# 添加执行权限
chmod +x deploy_aliyun_centos.sh

# 运行部署脚本
sudo bash deploy_aliyun_centos.sh
```

### 方法二：克隆仓库后部署
```bash
# 安装git
yum install -y git

# 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolbox

# 运行部署脚本
sudo bash deploy_aliyun_centos.sh
```

## 📦 部署过程说明

脚本将自动执行以下步骤：

### 1. 系统检测和修复
- 检测CentOS版本
- 修复CentOS 8 EOL仓库问题（如适用）
- 安装基础开发工具

### 2. 软件安装
- **Python 3.9**: 从官方源安装
- **PostgreSQL 15**: 生产级数据库
- **Redis**: 缓存和消息队列
- **Nginx**: Web服务器和反向代理

### 3. 项目部署
- 创建专用用户 `qatoolbox`
- 克隆最新代码
- 创建Python虚拟环境
- 安装项目依赖

### 4. 数据库配置
- 创建数据库和用户
- 执行数据库迁移
- 创建管理员账号

### 5. HTTPS配置
- 生成自签名SSL证书
- 配置Nginx反向代理
- 启用HTTPS重定向

### 6. 服务配置
- 创建systemd服务
- 配置自动启动
- 配置防火墙规则

## 🔐 安全配置

### SSL证书
部署脚本会自动生成自签名SSL证书，用于开发和测试。生产环境建议使用：

#### Let's Encrypt 免费证书
```bash
# 安装certbot
yum install -y certbot python3-certbot-nginx

# 获取证书（替换为您的域名）
certbot --nginx -d your-domain.com

# 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

#### 阿里云SSL证书
1. 在阿里云控制台购买SSL证书
2. 下载证书文件
3. 替换 `/home/qatoolbox/QAToolBox/ssl/` 目录下的证书文件
4. 重启Nginx: `systemctl restart nginx`

### 数据库安全
```bash
# 修改数据库密码
sudo -u postgres psql -c "ALTER USER qatoolbox PASSWORD 'your_strong_password';"

# 更新.env文件中的密码
vim /home/qatoolbox/QAToolBox/.env
```

### 系统安全
```bash
# 禁用root SSH登录
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# 启用防火墙
systemctl enable firewalld
systemctl start firewalld
```

## 🔧 部署后配置

### 1. 访问网站
部署完成后，您可以通过以下地址访问：
- **HTTPS**: `https://YOUR_SERVER_IP`
- **HTTP**: `http://YOUR_SERVER_IP` (自动重定向到HTTPS)

### 2. 管理员登录
- **用户名**: `admin`
- **密码**: `admin123`
- **建议**: 首次登录后立即修改密码

### 3. 域名配置（可选）
如果您有域名，需要：
1. 在域名服务商处添加A记录指向服务器IP
2. 修改Nginx配置文件 `/etc/nginx/conf.d/qatoolbox.conf`
3. 将 `server_name` 改为您的域名
4. 重启Nginx: `systemctl restart nginx`

### 4. 环境变量配置
编辑 `/home/qatoolbox/QAToolBox/.env` 文件：
```bash
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox  
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,YOUR_SERVER_IP

# 其他配置
REDIS_URL=redis://localhost:6379/0
```

## 📊 服务管理

### 查看服务状态
```bash
# 查看QAToolBox应用状态
sudo systemctl status qatoolbox

# 查看Nginx状态  
sudo systemctl status nginx

# 查看PostgreSQL状态
sudo systemctl status postgresql-15

# 查看Redis状态
sudo systemctl status redis
```

### 服务控制命令
```bash
# 启动/停止/重启QAToolBox
sudo systemctl start qatoolbox
sudo systemctl stop qatoolbox
sudo systemctl restart qatoolbox

# 查看应用日志
sudo journalctl -u qatoolbox -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 项目更新
使用提供的更新脚本：
```bash
cd /home/qatoolbox/QAToolBox
sudo -u qatoolbox bash update_project.sh
```

## 🔍 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 检查日志
sudo journalctl -u qatoolbox -n 50

# 检查端口占用
netstat -tulpn | grep :8000

# 手动测试
cd /home/qatoolbox/QAToolBox
sudo -u qatoolbox .venv/bin/python manage.py runserver 0.0.0.0:8000
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql-15

# 测试数据库连接
sudo -u qatoolbox psql -h localhost -U qatoolbox -d qatoolbox

# 重启数据库
sudo systemctl restart postgresql-15
```

#### 3. Nginx配置错误
```bash
# 测试Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 重新加载配置
sudo nginx -s reload
```

#### 4. SSL证书问题
```bash
# 检查证书文件
ls -la /home/qatoolbox/QAToolBox/ssl/

# 重新生成证书
cd /home/qatoolbox/QAToolBox
sudo openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

### 性能优化

#### 1. 数据库优化
```bash
# 编辑PostgreSQL配置
sudo vim /var/lib/pgsql/15/data/postgresql.conf

# 推荐配置（根据服务器内存调整）
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

#### 2. Nginx优化
```bash
# 编辑Nginx主配置
sudo vim /etc/nginx/nginx.conf

# 添加优化配置
worker_processes auto;
worker_connections 1024;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

#### 3. 应用优化
```bash
# 增加Gunicorn worker数量
sudo vim /etc/systemd/system/qatoolbox.service

# 修改ExecStart行中的--workers参数
--workers 8  # 通常为CPU核心数的2倍
```

## 📈 监控和备份

### 系统监控
```bash
# 安装htop
yum install -y htop

# 查看系统资源
htop
df -h
free -h
```

### 数据库备份
```bash
# 创建备份脚本
cat > /home/qatoolbox/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/qatoolbox/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump qatoolbox > $BACKUP_DIR/qatoolbox_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

chmod +x /home/qatoolbox/backup_db.sh

# 设置定时备份（每天凌晨2点）
echo "0 2 * * * /home/qatoolbox/backup_db.sh" | crontab -
```

### 日志管理
```bash
# 配置日志轮转
sudo vim /etc/logrotate.d/qatoolbox

# 添加配置
/var/log/qatoolbox/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 qatoolbox qatoolbox
    postrotate
        systemctl reload qatoolbox
    endscript
}
```

## 🆘 技术支持

如果在部署过程中遇到问题，请：

1. **查看日志**: 使用上述故障排除命令
2. **GitHub Issues**: 在项目仓库提交Issue
3. **文档更新**: 查看最新的部署文档

## 📝 更新日志

- **v1.0**: 初始版本，支持CentOS 7/8/9一键部署
- **v1.1**: 添加SSL证书配置和安全优化
- **v1.2**: 增加性能优化和监控配置

---

**祝您部署成功！** 🎉
