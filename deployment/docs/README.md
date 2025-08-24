# QAToolBox 部署文档

## 🚀 一键部署

### 快速开始

```bash
# 以root用户登录阿里云服务器
ssh root@47.103.143.152

# 运行一键部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deployment/scripts/one_click_deploy.sh | bash
```

### 支持的系统

- ✅ CentOS 7/8
- ✅ RHEL 7/8
- ✅ Rocky Linux 8/9
- ✅ AlmaLinux 8/9
- ✅ Ubuntu 18.04/20.04/22.04
- ✅ Debian 10/11

## 📋 部署信息

### 服务器信息
- **IP地址**: 47.103.143.152
- **域名**: shenyiqing.xin
- **系统**: CentOS/Ubuntu
- **安装目录**: /opt/QAToolbox

### 默认账户
| 服务 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 系统用户 | qatoolbox | qatoolbox123 | SSH登录/sudo操作 |
| Django管理 | admin | admin123456 | 网站后台管理 |
| PostgreSQL | qatoolbox | 自动生成 | 数据库连接 |

### 服务端口
| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80/443 | Web服务器 |
| Django | 8000 | Web应用 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存服务 |

## 🛠️ 服务管理

### 管理命令

```bash
cd /opt/QAToolbox

# 基本操作
./deployment/scripts/manage.sh start      # 启动服务
./deployment/scripts/manage.sh stop       # 停止服务
./deployment/scripts/manage.sh restart    # 重启服务
./deployment/scripts/manage.sh status     # 查看状态

# 日志和监控
./deployment/scripts/manage.sh logs       # 查看所有日志
./deployment/scripts/manage.sh logs web   # 查看web服务日志
./deployment/scripts/manage.sh health     # 健康检查

# 维护操作
./deployment/scripts/manage.sh update     # 更新代码
./deployment/scripts/manage.sh backup     # 备份数据库
./deployment/scripts/manage.sh cleanup    # 清理系统
./deployment/scripts/manage.sh ssl        # 配置SSL证书
```

### 手动Docker操作

```bash
cd /opt/QAToolbox

# 查看服务状态
docker-compose -f deployment/configs/docker-compose.yml ps

# 查看日志
docker-compose -f deployment/configs/docker-compose.yml logs -f

# 重启特定服务
docker-compose -f deployment/configs/docker-compose.yml restart web

# 进入容器
docker-compose -f deployment/configs/docker-compose.yml exec web bash
```

## 🔧 配置说明

### 环境变量

主要配置文件：`/opt/QAToolbox/.env`

```bash
# Django配置
DJANGO_SECRET_KEY=自动生成的密钥
DJANGO_DEBUG=False
ALLOWED_HOSTS=域名和IP列表

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=自动生成的密码

# 第三方API配置（可选）
DEEPSEEK_API_KEY=你的API密钥
GOOGLE_API_KEY=你的API密钥
# ... 其他API配置
```

### API密钥配置

如需使用特定功能，请在 `.env` 文件中配置相应的API密钥：

```bash
# 编辑环境变量
vim /opt/QAToolbox/.env

# 重启服务应用配置
./deployment/scripts/manage.sh restart
```

## 🔐 SSL证书配置

### 自动配置Let's Encrypt

```bash
cd /opt/QAToolbox
./deployment/scripts/manage.sh ssl
```

### 手动配置SSL

1. 获取SSL证书
2. 编辑 `deployment/configs/nginx.conf`
3. 取消SSL相关配置的注释
4. 重启Nginx服务

## 📊 监控和日志

### 日志位置

```bash
# 应用日志
/opt/QAToolbox/logs/

# Docker容器日志
docker-compose -f deployment/configs/docker-compose.yml logs

# 系统日志
/var/log/messages  # CentOS
/var/log/syslog    # Ubuntu
```

### 性能监控

```bash
# 系统资源
htop
df -h
free -h

# Docker资源
docker stats

# 服务状态
./deployment/scripts/manage.sh status
```

## 🔄 更新和维护

### 代码更新

```bash
cd /opt/QAToolbox
./deployment/scripts/manage.sh update
```

### 数据备份

```bash
# 自动备份
./deployment/scripts/manage.sh backup

# 备份文件位置
ls -la /opt/QAToolbox/backups/

# 恢复备份
./deployment/scripts/manage.sh restore /path/to/backup.sql.gz
```

### 系统清理

```bash
# 清理Docker资源和旧日志
./deployment/scripts/manage.sh cleanup
```

## 🆘 故障排除

### 常见问题

1. **服务启动失败**
```bash
# 查看详细日志
./deployment/scripts/manage.sh logs

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

2. **数据库连接失败**
```bash
# 检查数据库服务
docker-compose -f deployment/configs/docker-compose.yml ps db

# 查看数据库日志
docker-compose -f deployment/configs/docker-compose.yml logs db
```

3. **网站无法访问**
```bash
# 检查防火墙
firewall-cmd --list-all  # CentOS
ufw status               # Ubuntu

# 检查Nginx状态
docker-compose -f deployment/configs/docker-compose.yml ps nginx
```

### 健康检查

```bash
# 执行完整健康检查
./deployment/scripts/manage.sh health

# 手动检查各服务
curl http://localhost:8000/tools/health/
docker-compose -f deployment/configs/docker-compose.yml exec db pg_isready -U qatoolbox
docker-compose -f deployment/configs/docker-compose.yml exec redis redis-cli ping
```

## 📞 技术支持

### 重要文件位置

- 项目目录：`/opt/QAToolbox`
- 配置文件：`/opt/QAToolbox/.env`
- 日志目录：`/opt/QAToolbox/logs`
- 备份目录：`/opt/QAToolbox/backups`
- 部署配置：`/opt/QAToolbox/deployment/`

### 联系方式

- GitHub Issues: https://github.com/shinytsing/QAToolbox/issues
- 项目文档: https://github.com/shinytsing/QAToolbox

---

## 🎉 部署完成检查清单

- [ ] 服务器连接正常
- [ ] 所有服务启动成功
- [ ] 网站可以访问 (http://47.103.143.152)
- [ ] 管理后台可以登录 (http://shenyiqing.xin/admin/)
- [ ] SSL证书配置完成 (可选)
- [ ] 修改默认密码
- [ ] 配置必要的API密钥
- [ ] 设置定期备份
- [ ] 监控服务状态

**恭喜！您的QAToolBox已成功部署！**
