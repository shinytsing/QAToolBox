# 🚀 QAToolBox 中国一键部署 - 超简单版

## 📱 30秒快速部署

### 方法1: 一行命令部署 (最简单)

```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/install.sh | bash
```

### 方法2: 从GitHub克隆部署

```bash
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox
make install
```

### 方法3: 手动部署

```bash
wget https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh
chmod +x deploy_china.sh
./deploy_china.sh
```

## 🎯 部署完成后

访问: `http://你的服务器IP`

默认管理员:
- 用户名: `admin`
- 密码: `admin123456`

## 🛠️ 常用命令

```bash
# 使用Makefile (推荐)
make help          # 查看所有命令
make status        # 检查服务状态
make logs          # 查看日志
make restart       # 重启服务
make backup        # 备份数据
make update        # 更新代码

# 或使用docker-compose
docker-compose -f docker-compose.china.yml ps      # 查看状态
docker-compose -f docker-compose.china.yml logs -f # 查看日志
docker-compose -f docker-compose.china.yml restart # 重启
```

## 🚨 遇到问题？

1. **端口被占用**: `sudo netstat -tulpn | grep :80`
2. **Docker未安装**: 脚本会自动安装
3. **权限问题**: 确保不使用root用户运行
4. **网络问题**: 脚本使用中国镜像源，网络较慢时请耐心等待

## 📞 需要帮助？

查看详细文档: [DEPLOY_CHINA_README.md](DEPLOY_CHINA_README.md)

---
**就这么简单！** 🎉

