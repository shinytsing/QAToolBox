# QAToolBox 中国一键部署指南

## 🚀 快速开始

这是一个专为中国网络环境优化的Docker一键部署方案，适用于阿里云Ubuntu服务器。

### 📋 系统要求

- **操作系统**: Ubuntu 18.04+ (推荐 20.04 LTS)
- **内存**: 最少2GB，推荐4GB+
- **存储**: 最少10GB可用空间
- **网络**: 可访问互联网

### 🎯 一键部署

#### 方法1: 直接从GitHub部署 (推荐)

```bash
# 1. 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh | bash

# 或者使用国内镜像加速
curl -fsSL https://gitee.com/shinytsing/QAToolbox/raw/main/deploy_china.sh | bash
```

#### 方法2: 手动部署

```bash
# 1. 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox

# 2. 运行部署脚本
chmod +x deploy_china.sh
./deploy_china.sh
```

### 🔧 手动配置 (可选)

如果需要自定义配置，可以在运行部署脚本前进行以下操作：

#### 1. 配置环境变量

```bash
# 复制环境配置模板
cp env.template.china .env.production

# 编辑配置文件
nano .env.production
```

主要配置项：
- `ALLOWED_HOSTS`: 你的服务器IP或域名
- `SECRET_KEY`: Django密钥（脚本会自动生成）
- `DB_PASSWORD`: 数据库密码（脚本会自动生成）

#### 2. 自定义Docker配置

```bash
# 如果需要修改Docker配置
nano docker-compose.china.yml
```

### 📱 访问应用

部署完成后，你可以通过以下方式访问：

- **主应用**: `http://你的服务器IP`
- **管理后台**: `http://你的服务器IP/admin/`
- **默认管理员账号**: `admin`
- **默认管理员密码**: `admin123456`

⚠️ **重要**: 首次登录后请立即修改默认密码！

### 🛠️ 常用管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.china.yml ps

# 查看实时日志
docker-compose -f docker-compose.china.yml logs -f

# 重启服务
docker-compose -f docker-compose.china.yml restart

# 停止服务
docker-compose -f docker-compose.china.yml down

# 更新代码并重新部署
git pull origin main
docker-compose -f docker-compose.china.yml up -d --build

# 进入Web容器
docker-compose -f docker-compose.china.yml exec web bash

# 运行Django管理命令
docker-compose -f docker-compose.china.yml exec web python manage.py shell
```

### 🔒 安全配置

#### 1. 防火墙设置

```bash
# 安装UFW防火墙
sudo apt install ufw

# 允许SSH (重要!)
sudo ufw allow ssh

# 允许HTTP
sudo ufw allow 80

# 允许HTTPS (如果配置了SSL)
sudo ufw allow 443

# 启用防火墙
sudo ufw enable
```

#### 2. SSL证书配置 (可选)

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 🚨 故障排除

#### 常见问题

1. **Docker安装失败**
   ```bash
   # 手动安装Docker
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   # 重新登录或运行: newgrp docker
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose -f docker-compose.china.yml logs
   
   # 检查端口占用
   sudo netstat -tulpn | grep :80
   ```

3. **网络连接问题**
   ```bash
   # 测试网络连接
   ping mirrors.aliyun.com
   
   # 检查DNS
   nslookup mirrors.aliyun.com
   ```

4. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER ~/QAToolBox
   chmod -R 755 ~/QAToolBox
   ```

#### 日志文件位置

- Django应用日志: `logs/django.log`
- Nginx日志: `logs/nginx.log`
- 数据库日志: Docker容器内
- Redis日志: Docker容器内

### 📊 性能优化

#### 1. 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65535" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### 2. Docker优化

```bash
# 清理Docker缓存
docker system prune -f

# 优化镜像大小
docker-compose -f docker-compose.china.yml build --no-cache
```

### 🔄 更新部署

#### 自动更新脚本

```bash
#!/bin/bash
# 创建更新脚本
cat > update.sh << 'EOF'
#!/bin/bash
cd ~/QAToolBox
git pull origin main
docker-compose -f docker-compose.china.yml down
docker-compose -f docker-compose.china.yml up -d --build
echo "更新完成！"
EOF

chmod +x update.sh
```

#### 定时更新 (可选)

```bash
# 设置每天凌晨2点自动更新
crontab -e
# 添加: 0 2 * * * /home/yourusername/QAToolBox/update.sh >> /home/yourusername/update.log 2>&1
```

### 📞 技术支持

如果遇到问题，请：

1. 检查[故障排除](#🚨-故障排除)部分
2. 查看项目[Issues](https://github.com/yourusername/QAToolBox/issues)
3. 提交新的Issue并附上详细日志

### 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

## 🎉 恭喜！

如果你看到这里，说明部署已经成功！现在你可以：

- 🌐 访问你的应用
- 🔐 登录管理后台
- 📝 开始使用QAToolBox的各种功能
- 🚀 根据需要进行个性化配置

祝你使用愉快！ 🎊

