# QAToolBox 完整功能一键部署指南

## 🎯 重要说明
这个部署脚本**保持完整的URL导入**，不简化任何功能，确保所有Django应用和功能都能正常工作。

## 🚀 一键部署命令

### 方法1：直接执行（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_full_features.sh | sudo bash
```

### 方法2：下载后执行
```bash
# 下载脚本
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_full_features.sh

# 添加执行权限
chmod +x deploy_complete_full_features.sh

# 执行部署
sudo ./deploy_complete_full_features.sh
```

## 🎊 部署完成后访问

- **主域名**: http://shenyiqing.xin
- **备用域名**: http://www.shenyiqing.xin  
- **IP访问**: http://47.103.143.152
- **管理后台**: http://shenyiqing.xin/admin

### 管理员账户
- 用户名: `admin`
- 密码: `admin2024!`
- 邮箱: `admin@shenyiqing.xin`

## 🔧 脚本特性

### ✅ 完整功能保障
- **不简化URL导入** - 保持所有原始功能
- **完整Django应用加载** - apps.users, apps.tools, apps.content, apps.share
- **机器学习支持** - torch, torchvision, opencv-python等
- **图像识别功能** - 完整的real_image_recognition功能
- **异步任务支持** - Celery + Redis

### 🚀 技术栈
- **框架**: Django 4.2.7
- **数据库**: PostgreSQL + Redis
- **Web服务器**: Nginx + Gunicorn
- **进程管理**: Supervisor
- **Python环境**: 虚拟环境 + 阿里云镜像源
- **系统优化**: Ubuntu 24.04兼容 + 包冲突处理

### 📦 依赖支持
- **AI/ML**: torch, tensorflow, scikit-learn, opencv
- **图像处理**: Pillow, imageio, scikit-image
- **音频处理**: pydub, librosa, pyaudio
- **网络爬虫**: requests, beautifulsoup4, selenium, scrapy
- **文档处理**: PyPDF2, python-docx, openpyxl
- **环境配置**: python-dotenv, django-environ

## 🔍 部署验证

部署完成后会自动进行以下验证：
1. ✅ 服务状态检查（PostgreSQL, Redis, Nginx, Supervisor）
2. ✅ 端口监听检查（80, 8000, 5432, 6379）
3. ✅ 应用响应测试
4. ✅ Django应用加载验证

## 📋 常用管理命令

```bash
# 重启应用
sudo supervisorctl restart qatoolbox

# 查看应用日志
sudo tail -f /home/qatoolbox/logs/supervisor.log

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log

# Django管理命令
cd /home/qatoolbox/QAToolbox
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py [command]

# 重启服务
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart supervisor
```

## 🛠 故障排除

### 如果访问不了网站
```bash
# 检查服务状态
sudo systemctl status nginx
sudo supervisorctl status

# 检查端口监听
sudo netstat -tlnp | grep -E ":(80|8000)"

# 查看错误日志
sudo tail -f /home/qatoolbox/logs/supervisor.log
sudo tail -f /var/log/nginx/error.log
```

### 如果Django应用有问题
```bash
# 进入项目目录
cd /home/qatoolbox/QAToolbox

# 检查Django配置
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py check

# 重新迁移数据库
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py migrate

# 重新收集静态文件
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py collectstatic --noinput
```

## 🔄 更新部署

如果需要重新部署：
```bash
# 停止服务
sudo supervisorctl stop all

# 备份当前项目
cd /home/qatoolbox
sudo mv QAToolbox QAToolbox.backup.$(date +%Y%m%d_%H%M%S)

# 重新执行部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_full_features.sh | sudo bash
```

## 📞 支持

- **服务器**: 47.103.143.152
- **域名**: shenyiqing.xin
- **GitHub**: https://github.com/shinytsing/QAToolbox

---

*此脚本专门设计来保持Django应用的完整功能，确保所有URL导入和应用模块都能正常工作。*
