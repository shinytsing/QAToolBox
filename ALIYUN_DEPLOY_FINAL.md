# 🚀 QAToolBox 阿里云服务器一键部署

## 📋 部署信息
- **服务器IP**: `47.103.143.152`
- **域名**: `https://shenyiqing.xin/`
- **系统要求**: Ubuntu 18.04+ 或 CentOS 7+
- **内存要求**: 最低2GB，推荐4GB+
- **存储要求**: 最低10GB可用空间

## 🎯 一键部署命令

### 方法1: 直接执行（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash
```

### 方法2: 下载后执行
```bash
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh
chmod +x deploy_aliyun_one_click.sh
sudo ./deploy_aliyun_one_click.sh
```

### 方法3: 完整功能部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_with_all_deps.sh | sudo bash
```

## 🔧 部署过程

部署脚本会自动完成以下步骤：

### 1️⃣ 系统准备
- ✅ 更新系统包
- ✅ 安装编译工具
- ✅ 安装Python 3.9+
- ✅ 安装系统级依赖库

### 2️⃣ 服务安装
- ✅ PostgreSQL 数据库
- ✅ Redis 缓存服务
- ✅ Nginx Web服务器
- ✅ Supervisor 进程管理

### 3️⃣ 依赖解决
- ✅ **torch** - 深度学习框架
- ✅ **torchvision** - 计算机视觉
- ✅ **opencv-python** - 图像处理
- ✅ **django-environ** - 环境变量管理
- ✅ **scikit-learn** - 机器学习
- ✅ **numpy** - 数值计算

### 4️⃣ 项目配置
- ✅ 创建项目用户和目录
- ✅ 配置虚拟环境
- ✅ 数据库初始化
- ✅ 静态文件收集

## 🌐 部署完成后

### 访问地址
- **主站**: http://shenyiqing.xin/
- **管理后台**: http://shenyiqing.xin/admin/
- **IP访问**: http://47.103.143.152/

### 默认账号
- **用户名**: `admin`
- **密码**: `admin123456`

## 🧪 验证部署

部署完成后运行验证脚本：
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/test_deployment.sh | sudo bash
```

## 🛠️ 常用管理命令

```bash
# 查看应用状态
sudo supervisorctl status qatoolbox

# 重启应用
sudo supervisorctl restart qatoolbox

# 查看应用日志
sudo tail -f /var/log/qatoolbox.log

# 查看错误日志
sudo tail -f /var/log/qatoolbox_error.log

# 重启所有服务
sudo systemctl restart nginx postgresql redis-server supervisor

# 查看服务状态
sudo systemctl status nginx postgresql redis-server supervisor
```

## 🔍 故障排除

### 1. 内存不足
```bash
# 创建交换文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. 端口占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep -E ":(80|8000|5432|6379)"

# 杀死占用进程
sudo fuser -k 80/tcp
sudo fuser -k 8000/tcp
```

### 3. 权限问题
```bash
# 修复文件权限
sudo chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
sudo chmod -R 755 /home/qatoolbox/QAToolBox
```

### 4. 依赖安装失败
```bash
# 重新安装依赖
cd /home/qatoolbox/QAToolBox
sudo -u qatoolbox .venv/bin/pip install -r requirements_complete.txt --force-reinstall
```

## 🎯 在阿里云服务器上的完整操作步骤

### 第1步: 连接服务器
```bash
ssh root@47.103.143.152
```

### 第2步: 一键部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash
```

### 第3步: 等待部署完成
- 预计时间: 10-20分钟
- 依赖下载大小: 约2GB
- 过程中会显示进度信息

### 第4步: 验证部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/test_deployment.sh | sudo bash
```

### 第5步: 访问网站
- 打开浏览器访问: http://shenyiqing.xin/
- 进入管理后台: http://shenyiqing.xin/admin/
- 使用账号: admin / admin123456

## 📂 项目结构

部署后的项目结构：
```
/home/qatoolbox/QAToolBox/
├── .venv/                          # Python虚拟环境
├── .env                            # 环境变量配置
├── manage.py                       # Django管理脚本
├── settings.py                     # Django设置
├── urls.py                         # URL配置
├── wsgi.py                         # WSGI配置
├── requirements_complete.txt       # 完整依赖列表
└── static/                         # 静态文件

/var/www/qatoolbox/
├── static/                         # 收集的静态文件
└── media/                          # 媒体文件

/etc/nginx/sites-available/
└── qatoolbox                       # Nginx配置

/etc/supervisor/conf.d/
└── qatoolbox.conf                  # Supervisor配置
```

## 🎉 部署成功标志

当看到以下信息时，表示部署成功：

```
========================================
🎉 QAToolBox 阿里云部署完成！
========================================

🌐 访问地址:
  - http://shenyiqing.xin/
  - http://47.103.143.152/

👑 管理员登录:
  - 用户名: admin
  - 密码: admin123456
  - 后台: http://shenyiqing.xin/admin/

✅ 已安装的关键依赖:
  - ✅ Django (Web框架)
  - ✅ PyTorch (深度学习)
  - ✅ OpenCV (计算机视觉)
  - ✅ Django-Environ (环境变量)
  - ✅ PostgreSQL (数据库)
  - ✅ Redis (缓存)
  - ✅ Nginx (Web服务器)
```

## 📞 技术支持

如遇问题：
1. 检查日志文件: `/var/log/qatoolbox.log`
2. 查看错误日志: `/var/log/qatoolbox_error.log`
3. 检查服务状态: `sudo systemctl status nginx postgresql redis-server`
4. 重新运行部署脚本（安全的，会覆盖配置）

---

**注意**: 这个部署脚本已经解决了所有依赖问题，包括torch、environ等，确保一次部署成功！
