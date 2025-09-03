# QAToolBox Docker部署说明

## 🚀 快速开始

### 一键部署到阿里云

```bash
# 方法1: 直接运行（推荐）
curl -sSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/quick_deploy_aliyun.sh | bash

# 方法2: 下载后运行
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_docker.sh
chmod +x deploy_aliyun_docker.sh
./deploy_aliyun_docker.sh
```

## 📋 部署前准备

### 系统要求
- Ubuntu 20.04+ 或 Debian 10+
- 2GB+ RAM
- 10GB+ 磁盘空间
- 网络连接

### 服务器配置
1. 确保服务器可以访问外网
2. 开放必要端口：80, 443, 8000
3. 建议使用SSH密钥认证

## 🔧 部署步骤

### 1. 自动部署（推荐）

运行一键部署脚本，脚本会自动：
- 安装Docker和Docker Compose
- 配置防火墙
- 克隆项目代码
- 生成安全密钥
- 启动所有服务
- 初始化数据库

### 2. 手动部署

如果需要自定义配置，可以手动执行以下步骤：

```bash
# 1. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolbox

# 4. 配置环境变量
cp env.production .env
# 编辑.env文件，设置必要的配置

# 5. 启动服务
docker-compose up -d --build

# 6. 初始化数据库
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

## 🌐 访问应用

部署完成后，您可以通过以下方式访问：

- **应用地址**: `http://47.103.143.152:8000`
- **域名地址**: `http://shenyiqing.xin:8000`
- **管理后台**: `http://47.103.143.152:8000/admin/`
- **健康检查**: `http://47.103.143.152:8000/health/`

## 📊 服务管理

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
docker-compose down
```

## 🔄 更新部署

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

## 🛠️ 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

2. **权限问题**
   ```bash
   sudo chown -R $USER:$USER /opt/qatoolbox
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   # 增加swap空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### 日志分析

```bash
# 查看Docker日志
docker-compose logs web | tail -100

# 查看系统日志
sudo journalctl -u docker.service -f
```

## 🔒 安全配置

### 1. 更改默认密码
```bash
docker-compose exec web python manage.py changepassword admin
```

### 2. 配置SSL证书
```bash
# 将证书文件放在ssl_certs目录
# 取消注释nginx.conf中的HTTPS配置
```

### 3. 防火墙配置
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 📈 性能优化

### 1. 增加工作进程
编辑`docker-compose.yml`中的web服务配置：
```yaml
command: ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:application"]
```

### 2. 启用Redis缓存
在`.env`文件中配置：
```
REDIS_URL=redis://:your-redis-password@redis:6379/0
```

### 3. 数据库优化
```bash
# 创建数据库索引
docker-compose exec web python manage.py dbshell
```

## 📝 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django密钥 | 自动生成 |
| `DB_PASSWORD` | 数据库密码 | 自动生成 |
| `REDIS_PASSWORD` | Redis密码 | 自动生成 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 需要设置 |
| `ALLOWED_HOSTS` | 允许的主机 | localhost,127.0.0.1 |

## 🆘 获取帮助

如果遇到问题：

1. 查看[部署指南](DOCKER_DEPLOYMENT_GUIDE.md)
2. 检查[GitHub Issues](https://github.com/your-username/QAToolBox/issues)
3. 提交新的Issue

## 📄 许可证

本项目采用MIT许可证。