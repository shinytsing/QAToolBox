# QAToolBox 阿里云一键部署指南

## 🚀 快速开始

这是QAToolBox项目的最优化阿里云一键部署脚本，支持Ubuntu和CentOS系统。

### 📋 系统要求

- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Rocky Linux 8+
- **内存**: 至少2GB RAM（推荐4GB+）
- **磁盘**: 至少10GB可用空间
- **权限**: 需要root权限

### 🔧 一键部署

```bash
# 1. 下载部署脚本
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_ultimate.sh

# 2. 添加执行权限
chmod +x deploy_aliyun_ultimate.sh

# 3. 执行部署（需要root权限）
sudo bash deploy_aliyun_ultimate.sh
```

### 📦 自动安装的组件

- **Python 3.8+** 和开发环境
- **Django 4.2.7** Web框架
- **PostgreSQL** 数据库
- **Redis** 缓存服务
- **Nginx** Web服务器
- **Supervisor** 进程管理
- **PyTorch** 深度学习框架
- **OpenCV** 计算机视觉库
- **其他依赖** 机器学习相关库

### 🌐 部署完成后的访问

- **主页**: http://你的服务器IP/
- **管理后台**: http://你的服务器IP/admin/
- **默认管理员**: admin / admin123456

### 🔍 部署日志

部署过程中的详细日志保存在：`/var/log/qatoolbox_deploy.log`

### 🛠️ 常用管理命令

```bash
# 重启应用
sudo supervisorctl restart qatoolbox

# 查看应用状态
sudo supervisorctl status qatoolbox

# 查看应用日志
sudo tail -f /var/log/qatoolbox.log

# 重启Nginx
sudo systemctl restart nginx

# 重启数据库
sudo systemctl restart postgresql

# 重启Redis
sudo systemctl restart redis-server
```

### 📁 项目目录结构

```
/home/qatoolbox/QAToolBox/          # 项目主目录
├── .venv/                          # Python虚拟环境
├── manage.py                       # Django管理脚本
├── settings.py                     # Django配置文件
├── urls.py                         # URL路由配置
├── wsgi.py                         # WSGI应用入口
└── .env                            # 环境变量配置

/var/www/qatoolbox/                 # 静态文件目录
├── static/                         # 静态文件
└── media/                          # 媒体文件
```

### 🔒 安全配置

- 自动生成安全的Django SECRET_KEY
- 生产环境DEBUG=False
- 数据库密码加密存储
- 文件权限严格控制

### 🚨 故障排除

#### 1. 部署失败
```bash
# 查看详细日志
sudo tail -f /var/log/qatoolbox_deploy.log

# 检查服务状态
sudo systemctl status nginx postgresql redis-server supervisor
```

#### 2. pip wheel冲突问题
如果遇到 "Cannot uninstall wheel 0.42.0" 错误，可以使用专门的修复脚本：

```bash
# 下载并运行修复脚本
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/fix_pip_wheel_conflict.sh
chmod +x fix_pip_wheel_conflict.sh
sudo bash fix_pip_wheel_conflict.sh

# 或者手动修复
sudo python3 -m pip install --upgrade --force-reinstall --ignore-installed pip setuptools wheel
```

#### 3. 应用无法访问
```bash
# 检查应用进程
sudo supervisorctl status qatoolbox

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 重启应用
sudo supervisorctl restart qatoolbox
```

#### 4. 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查数据库连接
sudo -u postgres psql -c "\l"
```

### 📞 技术支持

如果遇到问题，请检查：
1. 系统日志：`/var/log/syslog` 或 `/var/log/messages`
2. 应用日志：`/var/log/qatoolbox.log`
3. 部署日志：`/var/log/qatoolbox_deploy.log`

### 🔄 更新部署

如需重新部署，直接运行部署脚本即可，脚本会自动清理旧环境并重新安装。

---

**注意**: 此脚本会完全重新配置系统环境，请在生产环境使用前做好备份。
