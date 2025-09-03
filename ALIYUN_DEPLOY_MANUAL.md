# QAToolBox 阿里云Docker部署手册

## 🎯 部署概述

本手册提供了将QAToolBox项目使用Docker部署到阿里云服务器的完整指南。

## 📦 已创建的文件

### Docker配置文件
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - 多容器编排配置
- `nginx.conf` - Nginx反向代理配置
- `init.sql` - PostgreSQL初始化脚本

### 部署脚本
- `deploy_aliyun_docker.sh` - 完整部署脚本
- `quick_deploy_aliyun.sh` - 快速部署脚本

### 环境配置
- `env.production` - 生产环境配置模板
- `.env.example` - 环境变量示例文件

### GitHub Actions
- `.github/workflows/docker-build.yml` - Docker镜像构建工作流
- `.github/workflows/deploy-aliyun.yml` - 阿里云自动部署工作流
- `.github/workflows/test.yml` - 测试工作流

### 文档
- `DOCKER_DEPLOYMENT_GUIDE.md` - 详细部署指南
- `README_DOCKER_DEPLOYMENT.md` - 快速部署说明
- `ALIYUN_DEPLOY_MANUAL.md` - 本手册

## 🚀 一键部署命令

### 方法1: 直接运行（推荐）
```bash
curl -sSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/quick_deploy_aliyun.sh | bash
```

### 方法2: 下载后运行
```bash
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_docker.sh
chmod +x deploy_aliyun_docker.sh
./deploy_aliyun_docker.sh
```

## 🔧 部署架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Django App    │    │   PostgreSQL    │
│   (Port 80)     │───▶│   (Port 8000)   │───▶│   (Port 5432)   │
│   Reverse Proxy │    │   Gunicorn      │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Port 6379)   │
                       │     Cache       │
                       └─────────────────┘
```

## 📋 系统要求

- **操作系统**: Ubuntu 20.04+ 或 Debian 10+
- **内存**: 至少2GB RAM
- **磁盘**: 至少10GB可用空间
- **网络**: 外网访问权限
- **端口**: 80, 443, 8000

## 🛠️ 部署步骤详解

### 1. 服务器准备
```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装必要工具
sudo apt-get install -y curl wget git
```

### 2. 自动部署
运行一键部署脚本，脚本会自动完成：
- Docker和Docker Compose安装
- 防火墙配置
- 项目代码克隆
- 环境变量配置
- 服务启动和初始化

### 3. 手动配置（可选）
如果需要自定义配置：

```bash
# 编辑环境变量
nano .env

# 主要配置项：
# - DJANGO_SECRET_KEY: Django密钥
# - DB_PASSWORD: 数据库密码
# - REDIS_PASSWORD: Redis密码
# - DEEPSEEK_API_KEY: DeepSeek API密钥
# - ALLOWED_HOSTS: 允许的主机
```

## 🌐 访问应用

部署完成后，通过以下地址访问：

- **应用首页**: `http://47.103.143.152:8000`
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
cd /opt/qatoolbox/QAToolBox

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

## 🔒 安全配置

### 1. 更改默认密码
```bash
docker-compose exec web python manage.py changepassword admin
```

### 2. 配置防火墙
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. SSL证书配置
```bash
# 将SSL证书放在ssl_certs目录
# 取消注释nginx.conf中的HTTPS配置
```

## 📈 性能优化

### 1. 增加工作进程
编辑`docker-compose.yml`：
```yaml
command: ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:application"]
```

### 2. 启用Redis缓存
在`.env`文件中配置：
```
REDIS_URL=redis://:your-redis-password@redis:6379/0
```

## 🛠️ 故障排除

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
   ```

### 日志分析
```bash
# 查看Docker日志
docker-compose logs web | tail -100

# 查看系统日志
sudo journalctl -u docker.service -f
```

## 📝 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django密钥 | 自动生成 |
| `DB_PASSWORD` | 数据库密码 | 自动生成 |
| `REDIS_PASSWORD` | Redis密码 | 自动生成 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 需要设置 |
| `ALLOWED_HOSTS` | 允许的主机 | localhost,127.0.0.1 |

## 🔄 GitHub Actions自动部署

项目配置了GitHub Actions工作流，支持：

1. **自动构建**: 推送代码时自动构建Docker镜像
2. **自动部署**: 推送到main分支时自动部署到阿里云
3. **自动测试**: 每次提交时自动运行测试

### 配置GitHub Secrets
在GitHub仓库设置中添加以下Secrets：
- `ALIYUN_HOST`: 阿里云服务器IP
- `ALIYUN_USERNAME`: SSH用户名
- `ALIYUN_SSH_KEY`: SSH私钥
- `ALIYUN_PORT`: SSH端口（默认22）

## 📊 监控和维护

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

## 🆘 获取帮助

如果遇到问题：

1. 查看[详细部署指南](DOCKER_DEPLOYMENT_GUIDE.md)
2. 检查[快速部署说明](README_DOCKER_DEPLOYMENT.md)
3. 查看[GitHub Issues](https://github.com/your-username/QAToolBox/issues)
4. 提交新的Issue

## 📄 许可证

本项目采用MIT许可证。

---

## 🎉 部署完成

恭喜！您已经成功配置了QAToolBox的Docker部署环境。现在您可以：

1. 将代码推送到GitHub
2. 在阿里云服务器上运行一键部署命令
3. 享受自动化的部署流程

如有任何问题，请参考相关文档或提交Issue。