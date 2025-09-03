# QAToolBox Docker部署指南

## 概述

本指南将帮助您在阿里云服务器上使用Docker部署QAToolBox项目。

## 系统要求

- Ubuntu 20.04+ 或 Debian 10+
- 至少2GB RAM
- 至少10GB可用磁盘空间
- 网络连接

## 快速部署

### 方法1: 一键部署脚本

```bash
# 下载并运行快速部署脚本
curl -sSL https://raw.githubusercontent.com/your-username/QAToolBox/main/quick_deploy_aliyun.sh | bash
```

### 方法2: 完整部署脚本

```bash
# 下载完整部署脚本
wget https://raw.githubusercontent.com/your-username/QAToolBox/main/deploy_aliyun_docker.sh
chmod +x deploy_aliyun_docker.sh
./deploy_aliyun_docker.sh
```

## 手动部署步骤

### 1. 安装Docker和Docker Compose

```bash
# 更新系统
sudo apt-get update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# 重新登录以应用用户组更改
exit
```

### 2. 克隆项目

```bash
# 创建项目目录
sudo mkdir -p /opt/qatoolbox
sudo chown $USER:$USER /opt/qatoolbox
cd /opt/qatoolbox

# 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolbox
```

### 3. 配置环境变量

```bash
# 复制环境配置文件
cp env.production .env

# 编辑环境变量
nano .env
```

主要配置项：
- `DJANGO_SECRET_KEY`: Django密钥（自动生成）
- `DB_PASSWORD`: 数据库密码（自动生成）
- `REDIS_PASSWORD`: Redis密码（自动生成）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `ALLOWED_HOSTS`: 允许的主机（添加您的域名或IP）

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 等待服务启动
sleep 30

# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

### 5. 配置防火墙

```bash
# 允许HTTP和HTTPS流量
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable
```

## 服务管理

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 更新部署

### 更新代码

```bash
# 进入项目目录
cd /opt/qatoolbox/QAToolbox

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

## 备份和恢复

### 备份数据库

```bash
# 创建备份目录
mkdir -p /opt/backups

# 备份数据库
docker-compose exec db pg_dump -U qatoolbox qatoolbox_production > /opt/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复数据库

```bash
# 恢复数据库
docker-compose exec -T db psql -U qatoolbox qatoolbox_production < /opt/backups/db_backup_20240101_120000.sql
```

### 备份媒体文件

```bash
# 备份媒体文件
tar -czf /opt/backups/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## 监控和维护

### 健康检查

```bash
# 检查应用健康状态
curl http://localhost:8000/health/

# 检查详细健康状态
curl http://localhost:8000/health/detailed/
```

### 系统监控

```bash
# 查看系统资源使用情况
docker stats

# 查看磁盘使用情况
df -h

# 查看内存使用情况
free -h
```

### 日志轮转

```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/docker-containers

# 添加以下内容：
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
```

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查日志
   docker-compose logs web
   
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   docker-compose ps db
   
   # 检查数据库日志
   docker-compose logs db
   ```

3. **静态文件无法访问**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   
   # 检查Nginx配置
   docker-compose logs nginx
   ```

### 性能优化

1. **增加工作进程**
   ```bash
   # 编辑docker-compose.yml
   # 修改web服务的command参数
   command: ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:application"]
   ```

2. **启用Redis缓存**
   ```bash
   # 在.env文件中配置Redis
   REDIS_URL=redis://:your-redis-password@redis:6379/0
   ```

## 安全建议

1. **更改默认密码**
   ```bash
   # 更改数据库密码
   docker-compose exec web python manage.py changepassword admin
   ```

2. **配置SSL证书**
   ```bash
   # 将SSL证书放在ssl_certs目录
   # 取消注释nginx.conf中的HTTPS配置
   ```

3. **定期更新**
   ```bash
   # 定期更新系统和Docker镜像
   sudo apt-get update && sudo apt-get upgrade
   docker-compose pull
   ```

## 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查GitHub Issues
3. 提交新的Issue

## 许可证

本项目采用MIT许可证。