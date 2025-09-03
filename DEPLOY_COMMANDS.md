# 阿里云部署命令指南

## 🚀 一键部署命令

### 方法1: 本地执行部署脚本
```bash
# 在本地项目目录执行
./deploy_to_aliyun.sh
```

### 方法2: 手动部署步骤

#### 1. 上传代码到服务器
```bash
# 使用rsync上传代码
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
    ./ admin@47.103.143.152:/var/www/qatoolbox/
```

#### 2. 连接到服务器
```bash
ssh admin@47.103.143.152
```

#### 3. 在服务器上执行部署
```bash
cd /var/www/qatoolbox
chmod +x deploy_aliyun_ubuntu.sh
./deploy_aliyun_ubuntu.sh
```

## 📋 部署脚本功能

### 系统环境配置
- ✅ Ubuntu系统更新
- ✅ 中国区pip源配置 (清华大学镜像)
- ✅ 基础依赖安装 (Python3, PostgreSQL, Redis, Nginx等)

### 数据库配置
- ✅ PostgreSQL安装和配置
- ✅ 创建数据库: `qatoolbox_production`, `qatoolbox_test`
- ✅ 创建用户: `qatoolbox` / `qatoolbox123`
- ✅ 数据库权限配置
- ✅ 数据库初始化 (所有字段默认值为空字符串)

### 应用配置
- ✅ Python虚拟环境创建
- ✅ 完整依赖安装 (requirements.txt)
- ✅ 系统级依赖安装 (OCR, 音频处理, 图像处理等)
- ✅ 环境变量配置
- ✅ 数据库迁移
- ✅ 静态文件收集
- ✅ 超级用户创建: `admin` / `admin123456`

### 服务配置
- ✅ Gunicorn配置
- ✅ Supervisor进程管理
- ✅ Nginx反向代理
- ✅ 防火墙配置
- ✅ 日志轮转配置
- ✅ 定时任务配置

## 🔧 部署后管理命令

### 服务管理
```bash
cd /var/www/qatoolbox

# 启动服务
./manage_qatoolbox.sh start

# 停止服务
./manage_qatoolbox.sh stop

# 重启服务
./manage_qatoolbox.sh restart

# 查看状态
./manage_qatoolbox.sh status

# 查看日志
./manage_qatoolbox.sh logs

# 更新应用
./manage_qatoolbox.sh update
```

### 数据库管理
```bash
# 连接数据库
sudo -u postgres psql -d qatoolbox_production

# 运行迁移
python manage.py migrate --settings=config.settings.aliyun_production

# 创建超级用户
python manage.py createsuperuser --settings=config.settings.aliyun_production
```

### 日志查看
```bash
# 应用日志
sudo tail -f /var/log/qatoolbox/supervisor.log

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 系统日志
sudo journalctl -u qatoolbox -f
```

## 🌐 访问信息

### 访问地址
- **本地访问**: http://localhost
- **外网访问**: http://47.103.143.152
- **域名访问**: http://shenyiqing.xin (需要配置DNS)

### 管理员账户
- **用户名**: admin
- **密码**: admin123456

### 数据库信息
- **数据库**: qatoolbox_production
- **用户**: qatoolbox
- **密码**: qatoolbox123
- **主机**: localhost:5432

## 🔒 安全配置

### SSL证书配置
```bash
# 安装SSL证书
sudo certbot --nginx -d shenyiqing.xin -d www.shenyiqing.xin

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 防火墙配置
```bash
# 查看防火墙状态
sudo ufw status

# 开放端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
```

## 📊 监控和维护

### 系统监控
```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
ps aux | grep qatoolbox
```

### 备份脚本
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/qatoolbox"
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -h localhost -U qatoolbox qatoolbox_production > $BACKUP_DIR/db_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/qatoolbox/media/

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 添加到定时任务
(crontab -l 2>/dev/null; echo "0 3 * * * /var/www/qatoolbox/backup.sh") | crontab -
```

## 🚨 故障排除

### 常见问题
1. **服务启动失败**: 检查日志 `./manage_qatoolbox.sh logs`
2. **数据库连接失败**: 检查PostgreSQL服务状态
3. **静态文件404**: 运行 `python manage.py collectstatic`
4. **权限问题**: 检查文件权限 `sudo chown -R $USER:$USER /var/www/qatoolbox`

### 重置服务
```bash
# 完全重置
sudo supervisorctl stop qatoolbox
sudo systemctl stop nginx
sudo systemctl stop postgresql
sudo systemctl stop redis-server

# 重新启动
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl start nginx
sudo supervisorctl start qatoolbox
```

---

**注意**: 部署完成后请及时修改默认密码并配置SSL证书！
