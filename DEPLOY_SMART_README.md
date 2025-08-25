# QAToolBox 智能部署脚本使用指南

## 🚀 快速解决502错误

你的网站出现502错误？使用以下步骤快速修复：

### 1. 快速修复502错误（推荐）

```bash
# 在阿里云服务器上执行
wget -O fix_502_error.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/fix_502_error.sh
sudo bash fix_502_error.sh
```

这个脚本会：
- ✅ 诊断所有服务状态
- ✅ 修复应用服务配置
- ✅ 修复Nginx配置
- ✅ 检查数据库和Redis连接
- ✅ 测试所有连接

### 2. 完整重新部署（如果快速修复无效）

```bash
# 在阿里云服务器上执行
wget -O deploy_smart_fix.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_smart_fix.sh
sudo bash deploy_smart_fix.sh
```

这个脚本会：
- ✅ 完全重新部署整个系统
- ✅ 备份现有配置
- ✅ 安装所有依赖
- ✅ 配置数据库和Redis
- ✅ 生成SSL证书
- ✅ 优化系统性能

## 🔧 常见问题解决

### 502错误的常见原因

1. **Gunicorn服务未启动**
   ```bash
   sudo systemctl status qatoolbox
   sudo systemctl restart qatoolbox
   ```

2. **端口8000未监听**
   ```bash
   sudo ss -tulpn | grep 8000
   sudo journalctl -u qatoolbox -f
   ```

3. **Nginx配置错误**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **数据库连接问题**
   ```bash
   sudo systemctl status postgresql
   PGPASSWORD="QAToolBox@2024" psql -h localhost -U qatoolbox -d qatoolbox -c "SELECT 1;"
   ```

### 手动检查步骤

```bash
# 1. 检查所有服务状态
sudo systemctl status qatoolbox nginx postgresql redis-server

# 2. 检查端口监听
sudo ss -tulpn | grep -E ":80|:443|:8000"

# 3. 查看应用日志
sudo journalctl -u qatoolbox -n 50

# 4. 查看Nginx日志
sudo tail -f /var/log/nginx/error.log

# 5. 测试本地连接
curl -I http://127.0.0.1:8000/health/
curl -I -k https://localhost/health/
```

## 📋 部署后管理

### 服务管理命令

```bash
# 重启应用
sudo systemctl restart qatoolbox

# 查看应用状态
sudo systemctl status qatoolbox

# 查看实时日志
sudo journalctl -u qatoolbox -f

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx
```

### 项目管理脚本

部署完成后，在项目目录 `/home/qatoolbox/QAToolBox/` 下会有以下管理脚本：

```bash
cd /home/qatoolbox/QAToolBox

# 查看服务状态
bash status.sh

# 重启服务
bash restart.sh

# 更新项目
bash update.sh
```

## 🌐 访问信息

- **网站地址**: https://shenyiqing.xin
- **管理后台**: https://shenyiqing.xin/admin/
- **健康检查**: https://shenyiqing.xin/health/

### 默认管理员账号
- **用户名**: `admin`
- **密码**: `QAToolBox@2024`

## 📁 重要文件位置

```
/home/qatoolbox/QAToolBox/          # 项目根目录
├── .env                            # 环境变量配置
├── ssl/                            # SSL证书
│   ├── cert.pem
│   └── key.pem
├── staticfiles/                    # 静态文件
├── media/                          # 媒体文件
└── .venv/                          # Python虚拟环境

/etc/nginx/sites-available/qatoolbox    # Nginx配置
/etc/systemd/system/qatoolbox.service   # 系统服务配置
/var/log/qatoolbox/                     # 应用日志
/var/log/nginx/                         # Nginx日志
```

## 🚨 故障排除

### 如果脚本执行失败

1. **检查网络连接**
   ```bash
   ping github.com
   curl -I https://github.com
   ```

2. **检查系统权限**
   ```bash
   whoami  # 确保是root用户
   sudo -i  # 切换到root
   ```

3. **查看详细错误**
   ```bash
   bash -x deploy_smart_fix.sh  # 显示详细执行过程
   ```

### 如果网站仍然无法访问

1. **检查防火墙**
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

2. **检查域名解析**
   ```bash
   nslookup shenyiqing.xin
   ping shenyiqing.xin
   ```

3. **检查SSL证书**
   ```bash
   openssl x509 -in /home/qatoolbox/QAToolBox/ssl/cert.pem -text -noout
   ```

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. 错误日志：`sudo journalctl -u qatoolbox -n 100`
2. Nginx日志：`sudo tail -n 50 /var/log/nginx/error.log`
3. 系统信息：`uname -a && lsb_release -a`
4. 服务状态：`sudo systemctl status qatoolbox nginx postgresql redis-server`

## 🔄 版本更新

定期更新项目：

```bash
cd /home/qatoolbox/QAToolBox
bash update.sh
```

或手动更新：

```bash
cd /home/qatoolbox/QAToolBox
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart qatoolbox
```

---

**注意**: 这些脚本专门为Ubuntu系统和你的项目配置设计，请确保在正确的环境中运行。
