# QAToolBox 一键部署脚本

## 🚀 阿里云服务器一键部署

### 服务器信息
- **服务器IP**: 47.103.143.152
- **域名**: https://shenyiqing.xin/
- **支持系统**: Ubuntu 18.04+, CentOS 7+

### 🎯 一键部署命令

```bash
# 下载并执行完整部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_with_all_deps.sh | sudo bash

# 或者分步执行
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_with_all_deps.sh
chmod +x deploy_complete_with_all_deps.sh
sudo ./deploy_complete_with_all_deps.sh
```

### 🔧 快速部署（最小安装）

```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_quick_start.sh | sudo bash
```

## 📋 部署内容

### ✅ 已解决的依赖问题
- **torch**: 深度学习框架 ✅
- **torchvision**: 计算机视觉 ✅  
- **opencv-python**: 图像处理 ✅
- **django-environ**: 环境变量管理 ✅
- **scikit-learn**: 机器学习 ✅
- **PostgreSQL**: 数据库 ✅
- **Redis**: 缓存系统 ✅
- **Nginx**: Web服务器 ✅

### 🏗️ 系统架构
```
用户请求 → Nginx (端口80/443) → Gunicorn (端口8000) → Django应用
                                      ↓
                               PostgreSQL (端口5432)
                                      ↓  
                                Redis (端口6379)
```

## 📂 项目文件结构

```
QAToolBox/
├── deploy_complete_with_all_deps.sh    # 完整部署脚本
├── deploy_quick_start.sh               # 快速部署脚本
├── test_deployment.sh                  # 部署测试脚本
├── requirements_complete.txt           # 完整依赖列表
├── env.production.complete             # 生产环境配置
├── DEPLOYMENT_GUIDE.md                 # 详细部署指南
└── README_DEPLOY.md                    # 本文件
```

## 🎯 部署后访问

- **主站**: https://shenyiqing.xin/
- **管理后台**: https://shenyiqing.xin/admin/
- **API文档**: https://shenyiqing.xin/api/docs/

### 默认管理员账号
- 用户名: `admin`
- 密码: `admin123456`

## 🔍 验证部署

```bash
# 下载并运行测试脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/test_deployment.sh | sudo bash
```

## 🛠️ 常用管理命令

```bash
# 重启应用
sudo supervisorctl restart qatoolbox

# 查看应用日志
sudo tail -f /var/log/qatoolbox.log

# 重启所有服务
sudo systemctl restart nginx postgresql redis-server supervisor

# 查看服务状态
sudo systemctl status nginx postgresql redis-server supervisor
```

## 🐛 故障排除

### 1. 依赖安装失败
```bash
# 重新安装Python依赖
cd /home/qatoolbox/QAToolBox
sudo -u qatoolbox .venv/bin/pip install -r requirements_complete.txt --force-reinstall
```

### 2. 数据库连接失败
```bash
# 重置数据库
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
```

### 3. 权限问题
```bash
# 修复文件权限
sudo chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
sudo chmod +x /home/qatoolbox/QAToolBox/manage.py
```

## 📞 技术支持

如遇问题请查看：
1. [详细部署指南](DEPLOYMENT_GUIDE.md)
2. 日志文件: `/var/log/qatoolbox.log`
3. GitHub Issues

---

**注意**: 确保服务器有足够的内存（建议2GB+）和磁盘空间（建议10GB+）
