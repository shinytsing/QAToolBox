# QAToolBox 阿里云CentOS部署指南

## 🚀 部署概览
本指南将帮助您在阿里云CentOS系统上部署QAToolBox项目，使用Docker容器化方案，确保稳定性和可扩展性。

## 📋 前置要求

### 服务器配置要求
- **操作系统**: CentOS 7.x 或 CentOS 8.x
- **最低配置**: 2核CPU，4GB内存，40GB硬盘
- **推荐配置**: 4核CPU，8GB内存，100GB硬盘
- **网络**: 公网IP，开放端口80、443、8000

### 必需的服务
- Docker
- Docker Compose
- Git
- Python 3.8+
- PostgreSQL 或 MySQL（可选，可使用Docker运行）

## 🔧 一、服务器初始化

### 1.1 更新系统
```bash
# 更新系统包
sudo yum update -y

# 安装基础工具
sudo yum install -y wget curl git vim htop
```

### 1.2 安装Docker
```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组（替换username为你的用户名）
sudo usermod -aG docker $USER

# 注销并重新登录，或者运行：
newgrp docker
```

### 1.3 安装Docker Compose
```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 创建软链接
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证安装
docker-compose --version
```

## 📦 二、项目部署

### 2.1 克隆项目
```bash
# 克隆项目到服务器
cd /opt
sudo git clone https://github.com/shinytsing/QAToolbox.git
sudo chown -R $USER:$USER QAToolbox
cd QAToolbox
```

### 2.2 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量（重要！）
vim .env
```

**重要配置项：**
```bash
# 基础配置
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,your-server-ip

# 数据库配置
DATABASE_URL=postgresql://user:password@db:5432/qatoolbox

# Redis配置
REDIS_URL=redis://redis:6379/0

# 邮件配置（可选）
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# 文件上传配置
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
```

### 2.3 生产环境Docker配置

创建生产环境Docker Compose文件：
```bash
vim docker-compose.prod.yml
```

### 2.4 构建并启动服务
```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

## 🗄️ 三、数据库初始化

### 3.1 数据库迁移
```bash
# 进入Django容器
docker-compose -f docker-compose.prod.yml exec web bash

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# 退出容器
exit
```

### 3.2 加载初始数据（可选）
```bash
# 如果有初始数据文件
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata initial_data.json
```

## 🌐 四、Nginx反向代理配置

### 4.1 安装Nginx
```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4.2 配置Nginx
```bash
sudo vim /etc/nginx/conf.d/qatoolbox.conf
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com your-server-ip;

    # 静态文件
    location /static/ {
        alias /opt/QAToolbox/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /opt/QAToolbox/media/;
        expires 7d;
    }

    # 代理到Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果使用）
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4.3 启用配置
```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 🔒 五、SSL证书配置（推荐）

### 5.1 安装Certbot
```bash
sudo yum install -y epel-release
sudo yum install -y certbot python3-certbot-nginx
```

### 5.2 获取SSL证书
```bash
# 自动配置SSL
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 六、系统服务配置

### 6.1 创建系统服务
```bash
sudo vim /etc/systemd/system/qatoolbox.service
```

添加以下内容：
```ini
[Unit]
Description=QAToolBox Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/QAToolbox
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### 6.2 启用服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable qatoolbox.service
sudo systemctl start qatoolbox.service
```

## 📊 七、监控和日志

### 7.1 查看应用日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs web

# 实时查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 7.2 系统监控
```bash
# 查看Docker容器状态
docker ps

# 查看系统资源使用
htop

# 查看磁盘使用
df -h
```

## 🔐 八、安全配置

### 8.1 防火墙配置
```bash
# 安装防火墙
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 开放必要端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=22/tcp

# 重载防火墙规则
sudo firewall-cmd --reload
```

### 8.2 定期备份
```bash
# 创建备份脚本
sudo vim /opt/backup.sh
```

添加以下内容：
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose -f /opt/QAToolbox/docker-compose.prod.yml exec -T db pg_dump -U postgres qatoolbox > $BACKUP_DIR/db_backup_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /opt/QAToolbox media/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# 添加执行权限
sudo chmod +x /opt/backup.sh

# 添加定时任务
sudo crontab -e
# 添加：每天凌晨2点备份
# 0 2 * * * /opt/backup.sh
```

## 🚀 九、部署后验证

### 9.1 功能检查
- [ ] 访问网站首页
- [ ] 用户注册/登录功能
- [ ] 工具功能正常
- [ ] 管理后台可访问
- [ ] 静态文件加载正常
- [ ] 数据库连接正常

### 9.2 性能优化
```bash
# 查看容器资源使用
docker stats

# 优化Docker镜像大小
docker system prune -a

# 配置日志轮转
docker-compose -f docker-compose.prod.yml config
```

## 🆘 十、故障排除

### 常见问题：

1. **容器启动失败**
   ```bash
   docker-compose -f docker-compose.prod.yml logs web
   ```

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串
   - 确认网络连接

3. **静态文件404**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```

4. **权限问题**
   ```bash
   sudo chown -R $USER:$USER /opt/QAToolbox
   ```

## 📞 技术支持

如遇到部署问题，请检查：
1. 服务器日志：`/var/log/messages`
2. Docker日志：`docker-compose logs`
3. Nginx日志：`/var/log/nginx/error.log`

---

🎉 **恭喜！您的QAToolBox已成功部署到阿里云CentOS服务器！**

记得定期更新系统和应用，保持安全性。
