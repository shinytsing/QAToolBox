# 阿里云部署指南

## 🚀 一键部署

在阿里云服务器上运行以下命令即可完成部署：

```bash
# 下载并运行一键部署脚本
curl -O https://raw.githubusercontent.com/yourusername/QAToolBox/main/aliyun_one_click_deploy.sh
chmod +x aliyun_one_click_deploy.sh
./aliyun_one_click_deploy.sh
```

## 📋 部署前准备

### 1. 服务器要求
- CentOS 7/8 或 Ubuntu 18.04+
- Python 3.9+
- 至少 2GB RAM
- 至少 10GB 磁盘空间

### 2. 安装Python和虚拟环境
```bash
# CentOS
sudo yum install python39 python39-pip python39-venv -y

# Ubuntu
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv -y
```

### 3. 克隆项目
```bash
cd /opt
git clone https://github.com/yourusername/QAToolBox.git
cd QAToolBox
```

### 4. 创建虚拟环境
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🛠️ 手动部署步骤

如果一键部署脚本遇到问题，可以按照以下步骤手动部署：

### 1. 运行诊断脚本
```bash
./diagnose_deployment.sh
```

### 2. 运行修复脚本
```bash
./fix_aliyun_deployment.sh
```

### 3. 使用一键部署脚本
```bash
./aliyun_one_click_deploy.sh
```

## 🔧 常见问题解决

### 问题1: Gunicorn启动失败
**症状**: `curl: (7) Failed to connect to localhost port 8000: Connection refused`

**解决方案**:
```bash
# 检查错误日志
tail -f /tmp/qatoolbox_error.log

# 手动启动测试
python manage.py runserver 0.0.0.0:8000
```

### 问题2: 数据库迁移失败
**症状**: `Your models in app(s): 'content', 'tools' have changes that are not yet reflected in a migration`

**解决方案**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 问题3: 静态文件重复警告
**症状**: `Found another file with the destination path...`

**解决方案**: 已在阿里云配置中修复，使用单一静态文件目录。

### 问题4: 端口被占用
**症状**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -tlnp | grep :8000
# 或
lsof -i :8000

# 杀死进程
pkill -f gunicorn
```

## 📊 服务管理

### 启动服务
```bash
./aliyun_one_click_deploy.sh
```

### 停止服务
```bash
pkill -f gunicorn
```

### 重启服务
```bash
pkill -f gunicorn
sleep 3
./aliyun_one_click_deploy.sh
```

### 查看服务状态
```bash
ps aux | grep gunicorn
netstat -tlnp | grep :8000
```

### 查看日志
```bash
# 访问日志
tail -f /tmp/qatoolbox_access.log

# 错误日志
tail -f /tmp/qatoolbox_error.log

# Django日志
tail -f /tmp/qatoolbox_django.log
```

## 🌐 访问应用

部署成功后，可以通过以下地址访问：

- **主页**: http://YOUR_SERVER_IP:8000
- **管理后台**: http://YOUR_SERVER_IP:8000/admin
  - 用户名: admin
  - 密码: admin123

## 🔒 安全建议

### 1. 修改默认密码
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('your_new_secure_password')
admin.save()
```

### 2. 配置防火墙
```bash
# CentOS
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload

# Ubuntu
ufw allow 8000
```

### 3. 使用Nginx反向代理（可选）
```bash
sudo yum install nginx -y  # CentOS
# 或
sudo apt install nginx -y  # Ubuntu
```

Nginx配置示例 (`/etc/nginx/sites-available/qatoolbox`):
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/QAToolbox/staticfiles/;
    }
    
    location /media/ {
        alias /opt/QAToolbox/media/;
    }
}
```

## 📞 技术支持

如遇到部署问题，请：

1. 运行诊断脚本: `./diagnose_deployment.sh`
2. 查看错误日志: `tail -20 /tmp/qatoolbox_error.log`
3. 提交Issue到GitHub仓库

## 📝 更新日志

- v1.0: 初始版本，支持SQLite数据库的简化部署
- v1.1: 修复静态文件重复问题
- v1.2: 优化错误处理和日志记录
