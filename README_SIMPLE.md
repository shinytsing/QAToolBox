# QAToolBox - 智能工具箱

一个简洁、强大的Django工具箱项目，提供AI工具、数据处理、API服务等功能。

## 🚀 一键部署

### 步骤1: 清理项目（可选）
```bash
# 如果项目有太多历史文件，先清理
wget -O cleanup_project.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/cleanup_project.sh
bash cleanup_project.sh
```

### 步骤2: 一键部署
```bash
# 下载部署脚本
wget -O deploy_simple.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_simple.sh

# 运行部署（需要root权限）
sudo bash deploy_simple.sh
```

### 步骤3: 启动服务
```bash
# 下载服务启动脚本
wget -O start_services.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/start_services.sh

# 启动所有服务
sudo bash start_services.sh
```

## 🎯 部署特点

- **超级简化**: 只安装必要的依赖，避免复杂的配置
- **稳定可靠**: 使用简化的Django配置，避免模块冲突
- **功能完整**: 包含管理后台、API接口、静态文件服务
- **美观界面**: 现代化的首页设计
- **智能检测**: 自动检测和解决常见问题

## 📊 系统要求

- **操作系统**: Ubuntu 18.04+ / CentOS 7+
- **Python**: 3.8+
- **内存**: 1GB+
- **磁盘**: 2GB+

## 🌐 访问地址

部署成功后：

- **首页**: http://shenyiqing.xin
- **管理后台**: http://shenyiqing.xin/admin/
- **API状态**: http://shenyiqing.xin/api/status/
- **健康检查**: http://shenyiqing.xin/api/health/

## 👤 默认账户

- **用户名**: admin
- **密码**: QAToolBox@2024

## 🔧 核心功能

### Django管理
- 完整的管理后台
- 用户权限管理
- 数据库管理

### API服务
- RESTful API接口
- JSON响应格式
- CORS跨域支持

### 静态文件
- 自动收集静态文件
- Nginx优化服务
- 缓存策略

### 数据库
- PostgreSQL数据库
- 自动迁移
- 备份支持

## 🛠️ 常用命令

### 服务管理
```bash
# 重启服务
sudo systemctl restart qatoolbox nginx

# 查看状态
sudo systemctl status qatoolbox nginx

# 查看日志
sudo journalctl -u qatoolbox -f
```

### 代码更新
```bash
cd /home/qatoolbox/QAToolbox
sudo -u qatoolbox git pull origin main
sudo systemctl restart qatoolbox
```

### Django管理
```bash
cd /home/qatoolbox/QAToolbox
sudo -u qatoolbox .venv/bin/python manage.py shell
sudo -u qatoolbox .venv/bin/python manage.py createsuperuser
```

## 🔍 故障排除

### 服务无法启动
```bash
# 查看详细日志
sudo journalctl -u qatoolbox --no-pager -n 50

# 检查配置
sudo -u qatoolbox /home/qatoolbox/QAToolbox/.venv/bin/python /home/qatoolbox/QAToolbox/manage.py check
```

### 数据库问题
```bash
# 重置数据库
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"

# 重新迁移
cd /home/qatoolbox/QAToolbox
sudo -u qatoolbox .venv/bin/python manage.py migrate
```

### Nginx配置
```bash
# 测试配置
sudo nginx -t

# 重新加载
sudo systemctl reload nginx
```

## 📦 技术栈

- **后端**: Django 4.2.7
- **数据库**: PostgreSQL
- **缓存**: Redis (可选)
- **Web服务器**: Nginx + Gunicorn
- **API**: Django REST Framework
- **静态文件**: WhiteNoise

## 📝 项目结构

```
QAToolBox/
├── apps/                 # Django应用
├── config/              # 配置文件
│   ├── settings/        # Django设置
│   └── wsgi.py         # WSGI配置
├── templates/           # 模板文件
├── static/             # 静态文件
├── requirements/       # 依赖文件
├── manage.py           # Django管理脚本
└── deploy_simple.sh    # 部署脚本
```

## 🤝 支持

如果遇到问题：

1. 查看日志: `sudo journalctl -u qatoolbox -f`
2. 检查服务状态: `sudo systemctl status qatoolbox nginx postgresql`
3. 重新运行部署脚本: `sudo bash deploy_simple.sh`

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**QAToolBox** - 让工具使用更简单，让部署更轻松！ 🎉
