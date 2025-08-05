# QAToolBox 阿里云部署总结

## 🎯 部署目标
将QAToolBox项目成功部署到阿里云服务器 `47.103.143.152`

## 📋 已完成的准备工作

### ✅ 1. 代码准备
- [x] 所有代码已推送到Git仓库
- [x] 项目结构完整，包含所有功能模块
- [x] 生产环境配置已准备就绪

### ✅ 2. 部署脚本
- [x] **完整部署脚本** `deploy_to_aliyun.sh`
  - 自动安装系统依赖（Python、PostgreSQL、Redis、Nginx）
  - 配置数据库和Web服务器
  - 部署项目代码并启动服务
  - 执行健康检查

- [x] **快速部署脚本** `quick_deploy.sh`
  - 适用于代码更新
  - 快速拉取代码并重启服务

- [x] **部署测试脚本** `test_deployment.py`
  - 测试健康检查、首页、管理员页面等
  - 验证部署是否成功

### ✅ 3. 配置文件
- [x] **生产环境配置** `config/settings/production.py`
  - 数据库配置（PostgreSQL）
  - 缓存配置（Redis）
  - 安全配置
  - 静态文件配置

- [x] **健康检查URL** `/health/`
  - 返回JSON格式的健康状态
  - 用于监控和负载均衡

### ✅ 4. 文档
- [x] **部署指南** `ALIYUN_DEPLOYMENT_GUIDE.md`
  - 详细的部署步骤
  - 故障排除指南
  - 安全建议
  - 维护指南

## 🚀 部署步骤

### 第一步：检查SSH连接
```bash
ssh admin@47.103.143.152 "echo 'SSH连接成功'"
```

### 第二步：执行完整部署
```bash
./deploy_to_aliyun.sh
```

### 第三步：验证部署
```bash
./test_deployment.py
```

## 📊 部署架构

```
用户请求 → Nginx (80/443) → Gunicorn (8000) → Django应用
                                    ↓
                              PostgreSQL数据库
                                    ↓
                              Redis缓存
```

## 🔧 服务配置

### Web服务器
- **Nginx**: 反向代理，静态文件服务
- **Gunicorn**: WSGI服务器，运行Django应用

### 数据库
- **PostgreSQL**: 主数据库
- **数据库名**: qatoolbox
- **用户名**: qatoolbox
- **密码**: qatoolbox123456

### 缓存
- **Redis**: 会话存储和缓存
- **端口**: 6379

### 系统服务
- **qatoolbox**: Gunicorn服务
- **nginx**: Web服务器
- **postgresql**: 数据库服务
- **redis-server**: 缓存服务

## 🌐 访问信息

### 网站地址
- **HTTP**: http://47.103.143.152
- **HTTPS**: https://47.103.143.152 (需要配置SSL证书)

### 管理员账号
- **用户名**: admin
- **密码**: admin123456
- **登录地址**: http://47.103.143.152/admin/

### 项目路径
- **项目目录**: `/home/admin/QAToolBox`
- **虚拟环境**: `/home/admin/QAToolBox/venv`
- **静态文件**: `/home/admin/QAToolBox/staticfiles`
- **媒体文件**: `/home/admin/QAToolBox/media`
- **日志文件**: `/home/admin/QAToolBox/logs`

## 🔍 监控和日志

### 查看服务状态
```bash
./quick_deploy.sh status
```

### 查看实时日志
```bash
ssh admin@47.103.143.152 "sudo journalctl -u qatoolbox -f"
```

### 健康检查
```bash
curl http://47.103.143.152/health/
```

## 🛠️ 常用管理命令

### 重启服务
```bash
ssh admin@47.103.143.152 "sudo systemctl restart qatoolbox"
ssh admin@47.103.143.152 "sudo systemctl restart nginx"
```

### 更新代码
```bash
./quick_deploy.sh deploy
```

### 进入项目目录
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox"
```

### 运行Django命令
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py [command]"
```

## 🔒 安全建议

### 1. 修改默认密码
部署后立即修改管理员密码：
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py changepassword admin"
```

### 2. 配置SSL证书
```bash
ssh admin@47.103.143.152 "sudo apt install certbot python3-certbot-nginx"
ssh admin@47.103.143.152 "sudo certbot --nginx -d your-domain.com"
```

### 3. 配置防火墙
```bash
ssh admin@47.103.143.152 "sudo ufw allow 22"
ssh admin@47.103.143.152 "sudo ufw allow 80"
ssh admin@47.103.143.152 "sudo ufw allow 443"
ssh admin@47.103.143.152 "sudo ufw enable"
```

## 📈 性能优化

### 1. 启用Gzip压缩
在Nginx配置中启用Gzip压缩。

### 2. 配置缓存
使用Redis缓存提高应用性能。

### 3. 数据库优化
定期维护PostgreSQL数据库。

## 🔄 备份策略

### 数据库备份
```bash
ssh admin@47.103.143.152 "cd /home/admin/QAToolBox && source venv/bin/activate && python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json"
```

### 媒体文件备份
```bash
ssh admin@47.103.143.152 "tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/"
```

## 📞 故障排除

### 服务无法启动
```bash
ssh admin@47.103.143.152 "sudo systemctl status qatoolbox"
ssh admin@47.103.143.152 "sudo journalctl -u qatoolbox -n 50"
```

### 网站无法访问
```bash
ssh admin@47.103.143.152 "sudo systemctl status nginx"
ssh admin@47.103.143.152 "sudo netstat -tlnp | grep :80"
```

### 数据库连接问题
```bash
ssh admin@47.103.143.152 "sudo systemctl status postgresql"
ssh admin@47.103.143.152 "sudo -u postgres psql -c '\\l'"
```

## 🎉 部署完成检查清单

- [ ] SSH连接正常
- [ ] 完整部署脚本执行成功
- [ ] 所有服务正常运行
- [ ] 网站可以正常访问
- [ ] 管理员页面可以访问
- [ ] 静态文件正常加载
- [ ] 健康检查通过
- [ ] 修改默认管理员密码
- [ ] 配置SSL证书（可选）
- [ ] 配置防火墙规则
- [ ] 设置定期备份

---

**部署完成后，您的QAToolBox项目就可以在阿里云服务器上正常运行了！**

🌐 **访问地址**: http://47.103.143.152
👤 **管理员账号**: admin
🔑 **管理员密码**: admin123456 