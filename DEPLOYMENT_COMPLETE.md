# 🎉 QAToolBox 中国一键部署方案 - 完整版

## 📦 已创建的文件清单

### 🐳 Docker 配置文件
- `Dockerfile.china` - 优化的中国网络环境Docker镜像
- `docker-compose.china.yml` - 完整的服务编排配置
- `docker-health-check.sh` - Docker健康检查脚本

### 🚀 部署脚本
- `deploy_china.sh` - 完整的一键部署脚本 (主要)
- `install.sh` - 超简单一键安装脚本
- `quick_deploy.sh` - 快速部署脚本

### ⚙️ 配置文件
- `env.template.china` - 环境变量配置模板
- `Makefile.china` - Make命令管理文件

### 🛠️ 运维脚本
- `backup.sh` - 数据备份脚本
- `monitor.sh` - 服务监控脚本

### 📚 文档
- `DEPLOY_CHINA_README.md` - 详细部署指南
- `QUICK_START_CHINA.md` - 快速开始指南

### 🔄 CI/CD
- `.github/workflows/deploy.yml` - GitHub Actions自动部署

## 🚀 三种部署方式

### 方式1: 超级简单 (推荐新手)
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/install.sh | bash
```

### 方式2: 使用Makefile (推荐运维)
```bash
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox
make install
```

### 方式3: 完整控制 (推荐开发者)
```bash
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox
chmod +x deploy_china.sh
./deploy_china.sh
```

## 🌟 方案特点

### ✅ 中国网络优化
- 使用阿里云Docker镜像源
- 使用阿里云Ubuntu软件源
- 使用阿里云pip镜像源
- 支持多个Docker镜像加速器

### ✅ 权限安全
- 非root用户运行
- 自动处理文件权限
- Docker用户组自动配置

### ✅ 依赖完整
- 自动安装Docker和Docker Compose
- 自动安装系统依赖
- 自动安装Python依赖
- 包含PostgreSQL和Redis

### ✅ 无脑安装
- 一键脚本自动化
- 智能环境检测
- 详细日志输出
- 错误自动处理

### ✅ 功能完整
- Web应用服务
- 数据库服务
- 缓存服务
- 静态文件服务
- 日志管理
- 健康检查

## 🛠️ 运维管理

### 日常命令 (使用Makefile)
```bash
make help      # 查看所有命令
make status    # 检查服务状态
make logs      # 查看实时日志
make restart   # 重启服务
make backup    # 备份数据
make update    # 更新代码
make monitor   # 持续监控
make clean     # 清理缓存
```

### 直接Docker命令
```bash
# 查看服务状态
docker-compose -f docker-compose.china.yml ps

# 查看日志
docker-compose -f docker-compose.china.yml logs -f

# 重启服务
docker-compose -f docker-compose.china.yml restart

# 进入容器
docker-compose -f docker-compose.china.yml exec web bash
```

## 📊 服务架构

```
┌─────────────────────────────────────────┐
│              Nginx (80端口)              │
│         静态文件 + 反向代理              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Django App (8000端口)          │
│              Web应用服务                │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌────▼────┐   ┌────▼────┐
│PostgreSQL│  │  Redis  │   │  Media  │
│  数据库   │  │  缓存   │   │  文件   │
└───────┘    └─────────┘   └─────────┘
```

## 🔧 自定义配置

### 环境变量配置
复制 `env.template.china` 为 `.env.production` 并修改：
```bash
cp env.template.china .env.production
nano .env.production
```

### Docker配置修改
编辑 `docker-compose.china.yml` 文件进行自定义配置。

## 📱 访问信息

部署完成后：
- **应用地址**: `http://你的服务器IP`
- **管理后台**: `http://你的服务器IP/admin/`
- **默认账号**: `admin` / `admin123456`

## 🚨 故障排除

### 常见问题
1. **端口占用**: `sudo netstat -tulpn | grep :80`
2. **Docker权限**: `sudo usermod -aG docker $USER` 然后重新登录
3. **防火墙**: `sudo ufw allow 80`
4. **日志查看**: `make logs` 或查看 `logs/` 目录

### 健康检查
```bash
./monitor.sh          # 运行监控脚本
make status           # 使用Makefile检查
curl http://localhost # 测试Web服务
```

## 🔄 持续集成

已配置GitHub Actions自动部署：
1. 推送代码到main分支
2. 自动触发部署
3. 服务器自动更新

需要在GitHub仓库设置以下Secrets：
- `SERVER_HOST`: 服务器IP
- `SERVER_USER`: 服务器用户名
- `SERVER_SSH_KEY`: SSH私钥

## 📈 性能优化

### 系统级优化
脚本已自动配置：
- Docker镜像加速
- 系统内核参数优化
- 文件描述符限制调整

### 应用级优化
- Nginx静态文件缓存
- Django静态文件压缩
- PostgreSQL连接池
- Redis缓存配置

## 🔐 安全建议

1. **修改默认密码**: 首次登录后立即修改
2. **配置防火墙**: 只开放必要端口
3. **SSL证书**: 生产环境建议配置HTTPS
4. **定期备份**: 使用 `make backup` 定期备份
5. **监控日志**: 定期检查错误日志

## 📞 技术支持

- **详细文档**: [DEPLOY_CHINA_README.md](DEPLOY_CHINA_README.md)
- **快速指南**: [QUICK_START_CHINA.md](QUICK_START_CHINA.md)
- **GitHub Issues**: 提交问题和建议

---

## 🎊 总结

这个部署方案提供了：
- ✅ **一键安装**: 真正的无脑部署
- ✅ **中国优化**: 专为中国网络环境设计
- ✅ **完整功能**: 包含所有必要组件
- ✅ **易于维护**: 丰富的运维工具
- ✅ **安全可靠**: 权限和安全配置
- ✅ **持续集成**: 自动化部署流程

**现在你可以轻松地在阿里云Ubuntu服务器上部署QAToolBox了！** 🚀

