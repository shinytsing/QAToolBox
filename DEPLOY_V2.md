# QAToolBox 一键部署指南 v2.0

## 🚀 快速开始

### 方法一：一键脚本部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/QAToolBox.git
cd QAToolBox

# 2. 运行一键部署脚本
./deploy.sh

# 3. 根据提示选择部署方式
# 1) 本地开发环境部署
# 2) 生产环境部署  
# 3) Docker容器部署
```

### 方法二：命令行直接部署

```bash
# 本地开发环境
./deploy.sh --local

# 生产环境
./deploy.sh --production

# Docker部署
./deploy.sh --docker
```

## 📋 部署方式对比

| 部署方式 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| 本地开发 | 开发测试 | 启动快，调试方便 | 不适合生产 |
| 生产部署 | 生产环境 | 性能好，稳定 | 配置复杂 |
| Docker部署 | 容器化环境 | 隔离性好，易扩展 | 需要Docker知识 |

## 🛠️ 系统要求

### 基础要求
- **操作系统**: Linux (CentOS/Ubuntu) / macOS
- **Python**: 3.9+ (推荐 3.11)
- **内存**: 最少 2GB，推荐 4GB+
- **磁盘**: 最少 10GB 可用空间

### 依赖服务
- **PostgreSQL**: 12+ (自动安装)
- **Redis**: 6+ (自动安装)
- **Docker**: 20+ (Docker部署时需要)

## 🔧 配置说明

### 环境变量配置

部署脚本会自动创建 `.env` 文件，主要配置项：

```bash
# Django核心配置
DJANGO_SECRET_KEY=自动生成
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=自动生成

# API密钥配置（需要手动设置）
DEEPSEEK_API_KEY=your-api-key
AMAP_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
```

### API密钥获取

1. **DeepSeek AI**: https://platform.deepseek.com/
2. **高德地图**: https://lbs.amap.com/
3. **OpenAI**: https://platform.openai.com/
4. **其他API**: 参考 `deploy/env.template`

## 🚀 部署流程详解

### 1. 本地开发环境部署

```bash
./deploy.sh --local
```

**执行步骤**：
1. 检查Python版本和系统环境
2. 安装系统依赖 (PostgreSQL, Redis)
3. 创建Python虚拟环境
4. 安装Python依赖包
5. 配置数据库和Redis
6. 生成环境配置文件
7. 执行Django迁移
8. 启动开发服务器

**访问地址**: http://localhost:8000

### 2. 生产环境部署

```bash
./deploy.sh --production
```

**与开发环境的区别**：
- 使用Gunicorn作为WSGI服务器
- 启用生产环境安全设置
- 优化静态文件服务
- 配置日志记录

### 3. Docker容器部署

```bash
./deploy.sh --docker
```

**容器架构**：
- `qatoolbox_web`: Django应用
- `qatoolbox_db`: PostgreSQL数据库
- `qatoolbox_redis`: Redis缓存
- `qatoolbox_celery`: 异步任务队列
- `qatoolbox_nginx`: 反向代理（可选）

## 🔍 部署验证

### 自动验证

部署脚本会自动进行以下验证：
- 服务进程状态检查
- HTTP响应测试
- 数据库连接测试
- Redis连接测试

### 手动验证

```bash
# 查看部署状态
./deploy.sh --status

# 检查服务日志
tail -f logs/*.log

# 测试API接口
curl http://localhost:8000/health/
curl http://localhost:8000/health/detailed/
```

## 🛠️ 服务管理

### 启动/停止服务

```bash
# 启动服务
./deploy.sh --start

# 停止服务  
./deploy.sh --stop

# 重启服务
./deploy.sh --restart

# 查看状态
./deploy.sh --status
```

### Docker服务管理

```bash
# 查看容器状态
docker-compose -f docker-compose.optimized.yml ps

# 查看日志
docker-compose -f docker-compose.optimized.yml logs -f

# 重启特定服务
docker-compose -f docker-compose.optimized.yml restart web
```

## 🐛 故障排除

### 常见问题

1. **Python版本不兼容**
   ```bash
   # 解决方案：安装Python 3.9+
   sudo yum install python39  # CentOS
   sudo apt install python3.9  # Ubuntu
   ```

2. **端口被占用**
   ```bash
   # 查看端口占用
   netstat -tlnp | grep :8000
   
   # 杀死占用进程
   pkill -f "runserver|gunicorn"
   ```

3. **数据库连接失败**
   ```bash
   # 检查PostgreSQL状态
   systemctl status postgresql
   
   # 重启PostgreSQL
   systemctl restart postgresql
   ```

4. **依赖包安装失败**
   ```bash
   # 清理虚拟环境重新安装
   rm -rf venv/
   ./deploy.sh --local
   ```

### 日志查看

```bash
# Django应用日志
tail -f logs/django.log

# Gunicorn服务日志
tail -f logs/gunicorn.log

# 系统服务日志
journalctl -u postgresql -f
journalctl -u redis -f
```

## 🔒 安全配置

### 生产环境安全检查

1. **修改默认密码**
   ```bash
   # 修改管理员密码
   python manage.py changepassword admin
   ```

2. **配置HTTPS**
   - 获取SSL证书
   - 配置Nginx反向代理
   - 启用HTTPS重定向

3. **防火墙配置**
   ```bash
   # 开放必要端口
   firewall-cmd --permanent --add-port=80/tcp
   firewall-cmd --permanent --add-port=443/tcp
   firewall-cmd --reload
   ```

## 📊 性能优化

### 生产环境优化建议

1. **数据库优化**
   - 配置连接池
   - 启用查询缓存
   - 定期备份数据

2. **缓存配置**
   - Redis持久化设置
   - 缓存策略优化
   - 内存使用监控

3. **静态文件优化**
   - CDN配置
   - Gzip压缩
   - 浏览器缓存

## 🔄 更新部署

### 代码更新

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新部署
./deploy.sh --restart

# 3. 数据库迁移（如有必要）
source venv/bin/activate
python manage.py migrate
```

### 依赖更新

```bash
# 更新Python依赖
source venv/bin/activate
pip install -r requirements/production.txt --upgrade

# 重启服务
./deploy.sh --restart
```

## 📞 技术支持

- **项目地址**: https://github.com/your-username/QAToolBox
- **问题反馈**: https://github.com/your-username/QAToolBox/issues
- **文档**: 查看项目 `docs/` 目录

## 📝 更新日志

### v2.0 (2024-08-24)
- ✅ 重构部署系统，支持多种部署方式
- ✅ 优化依赖管理，减少包冲突
- ✅ 添加Docker容器化支持
- ✅ 完善健康检查和监控
- ✅ 改进错误处理和日志记录

### v1.0 (之前版本)
- ✅ 基础功能实现
- ✅ 简单部署脚本
- ✅ 核心API接口
