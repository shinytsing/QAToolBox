# QAToolBox

一个基于Django的QA工具箱，提供多种实用工具和功能。

## 🚀 快速部署

### 阿里云一键部署

1. **克隆项目**
```bash
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox
```

2. **配置环境变量**
```bash
cp .env.production .env
# 编辑 .env 文件，配置你的API密钥和密码
```

3. **一键部署**
```bash
./deploy.sh
```

### 部署后访问

- **IP访问**: http://47.103.143.152
- **域名访问**: http://shenyiqing.xin
- **管理员账号**: admin / admin123

## 📋 功能特性

- 🔍 智能问答系统
- 📊 数据分析工具
- 🖼️ 图像处理工具
- 🎵 音频处理工具
- 📄 文档处理工具
- 🌐 网络爬虫工具
- 📈 数据可视化
- 🔐 用户认证系统

## 🛠️ 技术栈

- **后端**: Django 4.2 + Python 3.12
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **任务队列**: Celery
- **Web服务器**: Nginx
- **容器化**: Docker + Docker Compose

## 📁 项目结构

```
QAToolBox/
├── apps/                    # Django应用
├── config/                  # 配置文件
├── static/                  # 静态文件
├── media/                   # 媒体文件
├── templates/               # 模板文件
├── requirements.txt         # Python依赖
├── docker-compose.yml       # Docker编排
├── Dockerfile              # Docker镜像
├── nginx.production.conf   # Nginx配置
├── .env.production         # 生产环境变量
├── deploy.sh               # 部署脚本
├── backup.sh               # 备份脚本
└── monitor.sh              # 监控脚本
```

## 🔧 管理命令

### 部署
```bash
./deploy.sh
```

### 备份
```bash
./backup.sh
```

### 监控
```bash
./monitor.sh
```

### 查看日志
```bash
docker-compose logs -f web
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

## 🔐 环境变量配置

主要环境变量说明：

- `DJANGO_SECRET_KEY`: Django密钥
- `DB_PASSWORD`: 数据库密码
- `REDIS_PASSWORD`: Redis密码
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `GOOGLE_API_KEY`: Google API密钥
- `ALLOWED_HOSTS`: 允许的主机

## 📊 监控和日志

- 应用日志: `logs/django.log`
- Nginx日志: `docker-compose logs nginx`
- 数据库日志: `docker-compose logs db`
- Redis日志: `docker-compose logs redis`

## 🔄 备份策略

- 自动备份数据库、媒体文件、静态文件
- 保留最近7天的备份
- 备份文件存储在 `backups/` 目录

## 🆘 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   docker-compose logs web
   ```

2. **数据库连接失败**
   ```bash
   docker-compose exec db pg_isready -U qatoolbox
   ```

3. **静态文件404**
   ```bash
   docker-compose exec web python manage.py collectstatic
   ```

4. **权限问题**
   ```bash
   sudo chown -R $USER:$USER .
   ```

## 📞 支持

如有问题，请提交Issue或联系开发团队。

## 📄 许可证

MIT License
