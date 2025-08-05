# QAToolBox 阿里云服务器部署指南

## 服务器信息
- **IP地址**: 47.103.143.152
- **用户名**: admin
- **SSH端口**: 22

## 部署前准备

### 1. 本地环境准备
确保本地项目已经推送到Git仓库：
```bash
git add .
git commit -m "准备部署到阿里云"
git push origin main
```

### 2. SSH密钥配置
确保您的SSH密钥已经配置到服务器：
```bash
# 检查SSH连接
ssh admin@47.103.143.152 "echo 'SSH连接成功'"
```

## 部署方式

### 方式一：完整部署（首次部署）
使用完整部署脚本，会自动安装所有依赖和配置服务：

```bash
./deploy_to_aliyun.sh
```

这个脚本会：
- 检查本地Git状态
- 推送代码到远程仓库
- 在服务器上安装系统依赖（Python、PostgreSQL、Redis、Nginx）
- 配置数据库
- 配置Nginx反向代理
- 配置Gunicorn服务
- 部署项目代码
- 启动所有服务
- 执行健康检查

### 方式二：快速部署（后续更新）
使用快速部署脚本，适用于代码更新：

```bash
./quick_deploy.sh deploy
```

这个脚本会：
- 推送代码到Git仓库
- 在服务器上拉取最新代码
- 安装Python依赖
- 运行数据库迁移
- 收集静态文件
- 重启服务

## 服务管理

### 检查服务状态
```bash
./quick_deploy.sh status
```

### 查看服务日志
```bash
./quick_deploy.sh logs
```

### 手动重启服务
```bash
ssh admin@47.103.143.152 "sudo systemctl restart qatoolbox"
ssh admin@47.103.143.152 "sudo systemctl restart nginx"
```

## 部署后信息

### 访问信息
- **网站地址**: http://47.103.143.152
- **管理员账号**: admin
- **管理员密码**: admin123456

### 项目路径
- **项目目录**: /home/admin/QAToolBox
- **虚拟环境**: /home/admin/QAToolBox/venv
- **静态文件**: /home/admin/QAToolBox/staticfiles
- **媒体文件**: /home/admin/QAToolBox/media
- **日志文件**: /home/admin/QAToolBox/logs

### 数据库信息
- **数据库类型**: PostgreSQL
- **数据库名**: qatoolbox
- **用户名**: qatoolbox
- **密码**: qatoolbox123456

## 常用命令

### 进入项目目录
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox"
```

### 激活虚拟环境
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate"
```

### 运行Django管理命令
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py [command]"
```

### 查看实时日志
```bash
ssh admin@47.103.143.152 "sudo journalctl -u qatoolbox -f"
```

## 故障排除

### 1. 服务无法启动
检查服务状态：
```bash
ssh admin@47.103.143.152 "sudo systemctl status qatoolbox"
```

查看错误日志：
```bash
ssh admin@47.103.143.152 "sudo journalctl -u qatoolbox -n 50"
```

### 2. 网站无法访问
检查Nginx状态：
```bash
ssh admin@47.103.143.152 "sudo systemctl status nginx"
```

检查端口监听：
```bash
ssh admin@47.103.143.152 "sudo netstat -tlnp | grep :80"
ssh admin@47.103.143.152 "sudo netstat -tlnp | grep :8000"
```

### 3. 数据库连接问题
检查PostgreSQL状态：
```bash
ssh admin@47.103.143.152 "sudo systemctl status postgresql"
```

测试数据库连接：
```bash
ssh admin@47.103.143.152 "sudo -u postgres psql -c '\\l'"
```

### 4. 静态文件问题
重新收集静态文件：
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py collectstatic --noinput"
```

## 安全建议

### 1. 修改默认密码
部署后立即修改管理员密码：
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py changepassword admin"
```

### 2. 配置SSL证书
为生产环境配置HTTPS：
```bash
# 安装Certbot
ssh admin@47.103.143.152 "sudo apt install certbot python3-certbot-nginx"

# 获取SSL证书（需要域名）
ssh admin@47.103.143.152 "sudo certbot --nginx -d your-domain.com"
```

### 3. 防火墙配置
配置防火墙规则：
```bash
ssh admin@47.103.143.152 "sudo ufw allow 22"
ssh admin@47.103.143.152 "sudo ufw allow 80"
ssh admin@47.103.143.152 "sudo ufw allow 443"
ssh admin@47.103.143.152 "sudo ufw enable"
```

## 备份和恢复

### 备份数据库
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json"
```

### 备份媒体文件
```bash
ssh admin@47.103.143.152 "tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/"
```

### 恢复数据库
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py loaddata backup_file.json"
```

## 性能优化

### 1. 启用Gzip压缩
在Nginx配置中启用Gzip压缩以提高性能。

### 2. 配置缓存
使用Redis缓存提高应用性能。

### 3. 数据库优化
定期维护PostgreSQL数据库：
```bash
ssh admin@47.103.143.152 "sudo -u postgres vacuumdb --all --analyze"
```

## 监控和维护

### 1. 设置日志轮转
配置日志文件自动轮转以防止磁盘空间不足。

### 2. 监控系统资源
定期检查服务器资源使用情况：
```bash
ssh admin@47.103.143.152 "htop"
ssh admin@47.103.143.152 "df -h"
ssh admin@47.103.143.152 "free -h"
```

### 3. 定期更新
定期更新系统和依赖包：
```bash
ssh admin@47.103.143.152 "sudo apt update && sudo apt upgrade -y"
```

---

**注意**: 部署完成后，请及时修改默认密码并配置SSL证书以确保生产环境的安全性。 