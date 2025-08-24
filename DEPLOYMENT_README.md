# QAToolBox 阿里云一键部署

## 🚀 快速开始

在阿里云服务器上运行一条命令即可完成部署：

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/QAToolBox/main/deploy_aliyun_final.sh | bash
```

或者下载脚本后运行：

```bash
wget https://raw.githubusercontent.com/yourusername/QAToolBox/main/deploy_aliyun_final.sh
chmod +x deploy_aliyun_final.sh
./deploy_aliyun_final.sh
```

## 📋 系统要求

- **操作系统**: CentOS 7/8, Ubuntu 18.04+, 或其他Linux发行版
- **Python**: 3.8+ (推荐3.9+)
- **内存**: 最少1GB RAM (推荐2GB+)
- **磁盘**: 最少2GB可用空间
- **网络**: 能够访问外网下载依赖包

## ⚡ 部署特性

- ✅ **全自动部署**: 一键完成所有配置
- ✅ **依赖检查**: 自动检查系统要求
- ✅ **错误处理**: 详细的错误提示和日志
- ✅ **服务管理**: 自动配置Gunicorn服务
- ✅ **安全配置**: 优化的生产环境设置
- ✅ **状态验证**: 部署后自动验证服务状态

## 🛠️ 部署过程

脚本会自动执行以下步骤：

1. **系统检查**: 验证操作系统、Python版本、磁盘空间等
2. **依赖安装**: 安装必要的系统包和Python包
3. **项目设置**: 克隆或更新项目代码
4. **环境配置**: 创建Python虚拟环境并安装依赖
5. **Django配置**: 数据库迁移、静态文件收集、创建管理员用户
6. **服务启动**: 启动Gunicorn Web服务器
7. **部署验证**: 测试服务是否正常运行

## 🌐 访问应用

部署成功后，通过以下地址访问：

- **主页**: `http://YOUR_SERVER_IP:8000`
- **管理后台**: `http://YOUR_SERVER_IP:8000/admin`
  - 用户名: `admin`
  - 密码: `admin123`

## 📊 服务管理

### 查看服务状态
```bash
ps aux | grep gunicorn
netstat -tlnp | grep :8000
```

### 查看日志
```bash
# 错误日志
tail -f /tmp/qatoolbox_error.log

# 访问日志
tail -f /tmp/qatoolbox_access.log

# Django日志
tail -f /tmp/qatoolbox_django.log
```

### 重启服务
```bash
pkill -f gunicorn
./deploy_aliyun_final.sh
```

### 停止服务
```bash
pkill -f gunicorn
```

## 🔧 故障排除

### 常见问题

1. **端口8000被占用**
   ```bash
   netstat -tlnp | grep :8000
   pkill -f gunicorn
   ```

2. **Python版本不兼容**
   ```bash
   # CentOS
   sudo yum install python39 python39-pip python39-venv

   # Ubuntu
   sudo apt install python3.9 python3.9-pip python3.9-venv
   ```

3. **权限问题**
   ```bash
   sudo chown -R $(whoami):$(whoami) /opt/QAToolBox
   ```

4. **防火墙阻止访问**
   ```bash
   # CentOS
   sudo firewall-cmd --permanent --add-port=8000/tcp
   sudo firewall-cmd --reload

   # Ubuntu
   sudo ufw allow 8000
   ```

### 诊断工具

项目提供了额外的诊断和修复脚本：

```bash
# 运行诊断
./diagnose_deployment.sh

# 运行修复
./fix_aliyun_deployment.sh

# 简化部署
./aliyun_one_click_deploy.sh
```

## 🔒 安全建议

1. **修改默认密码**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   admin = User.objects.get(username='admin')
   admin.set_password('your_secure_password')
   admin.save()
   ```

2. **配置防火墙**
   - 只开放必要的端口 (22, 80, 443, 8000)
   - 使用密钥认证SSH

3. **使用HTTPS**
   - 配置SSL证书
   - 使用Nginx反向代理

4. **定期更新**
   - 更新系统包
   - 更新Python依赖

## 📚 更多文档

- [详细部署指南](./ALIYUN_DEPLOYMENT_GUIDE.md)
- [配置说明](./config/settings/aliyun.py)
- [故障排除](./ALIYUN_DEPLOYMENT_GUIDE.md#-常见问题解决)

## 🤝 支持

如果遇到问题：

1. 查看[部署指南](./ALIYUN_DEPLOYMENT_GUIDE.md)
2. 运行诊断脚本: `./diagnose_deployment.sh`
3. 查看错误日志: `tail -20 /tmp/qatoolbox_error.log`
4. 提交Issue到GitHub仓库

## 📝 更新日志

- **v1.0** (2024-01-XX): 初始发布
  - 支持CentOS/Ubuntu自动部署
  - SQLite数据库配置
  - Gunicorn Web服务器
  - 完整的错误处理和日志记录