# QAToolBox 阿里云部署指南

## 一键部署

在你的阿里云服务器上运行以下命令即可完成部署：

```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/aliyun_deploy.sh | bash
```

## 服务器信息

- **服务器IP**: 47.103.143.152
- **域名**: shenyiqing.xin
- **操作系统**: Ubuntu 20.04+ 推荐

## 部署内容

脚本会自动完成以下操作：

1. ✅ 更新系统包
2. ✅ 安装Docker和Docker Compose
3. ✅ 安装Nginx和Certbot
4. ✅ 配置防火墙
5. ✅ 克隆项目代码
6. ✅ 创建环境配置
7. ✅ 构建Docker镜像
8. ✅ 启动所有服务
9. ✅ 创建系统服务

## 服务架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│   Django Web    │────│   PostgreSQL    │
│   (反向代理)     │    │     (主应用)     │    │    (数据库)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Celery Worker  │────│     Redis       │
                       │   (异步任务)     │    │    (缓存)       │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │  Celery Beat    │
                       │   (定时任务)     │
                       └─────────────────┘
```

## 访问地址

部署完成后，可通过以下地址访问：

- **主站**: http://47.103.143.152 或 http://shenyiqing.xin
- **管理后台**: http://shenyiqing.xin/admin/

## 默认账户

- **用户名**: admin
- **密码**: admin123456
- **邮箱**: admin@shenyiqing.xin

⚠️ **请立即修改默认密码！**

## 服务管理

部署完成后，使用以下命令管理服务：

```bash
# 进入项目目录
cd ~/QAToolbox

# 启动服务
./manage_service.sh start

# 停止服务
./manage_service.sh stop

# 重启服务
./manage_service.sh restart

# 查看服务状态
./manage_service.sh status

# 查看日志
./manage_service.sh logs

# 更新服务
./manage_service.sh update

# 备份数据库
./manage_service.sh backup

# 配置SSL证书
./manage_service.sh ssl
```

## SSL证书配置

如需启用HTTPS，请执行：

```bash
cd ~/QAToolbox
./manage_service.sh ssl
```

然后编辑nginx配置文件，取消SSL相关配置的注释：

```bash
# 编辑配置
nano nginx/nginx.conf

# 取消以下行的注释：
# ssl_certificate /etc/letsencrypt/live/shenyiqing.xin/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/shenyiqing.xin/privkey.pem;

# 重启服务
./manage_service.sh restart
```

## 系统服务

脚本会自动创建系统服务，服务器重启后自动启动：

```bash
# 查看服务状态
sudo systemctl status qatoolbox

# 手动启动
sudo systemctl start qatoolbox

# 手动停止
sudo systemctl stop qatoolbox
```

## 监控和维护

### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看资源使用
```bash
docker stats
```

### 查看磁盘使用
```bash
df -h
docker system df
```

### 清理Docker
```bash
docker system prune -a
```

### 备份重要数据
```bash
# 备份数据库
./manage_service.sh backup

# 备份媒体文件
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# 备份环境配置
cp .env .env.backup
```

## 故障排除

### 服务无法启动
```bash
# 查看详细日志
./manage_service.sh logs

# 检查Docker状态
sudo systemctl status docker

# 重启Docker
sudo systemctl restart docker
```

### 端口冲突
```bash
# 查看端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# 停止占用端口的服务
sudo systemctl stop apache2  # 如果安装了Apache
```

### 内存不足
```bash
# 查看内存使用
free -h

# 添加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 磁盘空间不足
```bash
# 清理Docker镜像和容器
docker system prune -a

# 清理日志
sudo journalctl --vacuum-time=7d
```

## 性能优化

### 数据库优化
```bash
# 进入数据库容器
docker-compose -f docker-compose.prod.yml exec db psql -U qatoolbox

# 查看数据库大小
SELECT pg_size_pretty(pg_database_size('qatoolbox'));

# 清理过期数据
VACUUM ANALYZE;
```

### 静态文件优化
```bash
# 重新收集静态文件
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --clear --noinput
```

## 更新部署

```bash
cd ~/QAToolbox

# 拉取最新代码
git pull origin main

# 更新服务
./manage_service.sh update
```

## 安全建议

1. **修改默认密码**: 立即修改admin账户密码
2. **启用SSL**: 配置HTTPS加密
3. **定期备份**: 设置自动备份计划
4. **监控日志**: 定期检查错误日志
5. **更新系统**: 定期更新系统和软件包

## 联系支持

如遇到问题，请：

1. 查看日志: `./manage_service.sh logs`
2. 检查服务状态: `./manage_service.sh status`
3. 查看系统资源: `htop` 或 `docker stats`

---

**部署完成！享受使用QAToolBox！** 🎉
