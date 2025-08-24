# 🚀 QAToolBox 快速开始指南

## ⚡ 30秒快速部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/QAToolBox.git
cd QAToolBox

# 2. 一键部署
./deploy.sh

# 3. 访问应用
# 🌐 网站: http://localhost:8000
# 👤 管理后台: http://localhost:8000/admin/
# 📋 用户名: admin
# 🔑 密码: admin123
```

## 📋 三种部署方式

### 🔧 方式一：本地开发环境（推荐新手）
```bash
./deploy.sh --local
```
- ✅ 启动最快（5-10分钟）
- ✅ 适合开发和测试
- ✅ 支持热重载

### 🏭 方式二：生产环境
```bash
./deploy.sh --production
```
- ✅ 性能最优
- ✅ 适合正式使用
- ✅ 安全配置完善

### 🐳 方式三：Docker容器
```bash
./deploy.sh --docker
```
- ✅ 环境隔离
- ✅ 易于扩展
- ✅ 支持集群部署

## 🛠️ 常用命令

```bash
# 服务管理
./deploy.sh --start    # 启动服务
./deploy.sh --stop     # 停止服务  
./deploy.sh --restart  # 重启服务
./deploy.sh --status   # 查看状态

# 查看日志
tail -f logs/django.log      # Django日志
tail -f logs/gunicorn.log    # Web服务日志

# 健康检查
curl http://localhost:8000/health/          # 基础检查
curl http://localhost:8000/health/detailed/ # 详细检查
```

## 🔧 配置API密钥

编辑 `.env` 文件，配置你的API密钥：

```bash
# AI服务
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key

# 地图服务  
AMAP_API_KEY=your-amap-key

# 图片服务
PEXELS_API_KEY=your-pexels-key
UNSPLASH_API_KEY=your-unsplash-key
```

## 🐛 遇到问题？

### 常见问题快速解决

1. **端口被占用**
   ```bash
   pkill -f "runserver|gunicorn"
   ./deploy.sh --restart
   ```

2. **依赖安装失败**
   ```bash
   rm -rf venv/
   ./deploy.sh --local
   ```

3. **数据库连接失败**
   ```bash
   systemctl restart postgresql
   ./deploy.sh --restart
   ```

4. **查看详细错误**
   ```bash
   ./deploy.sh --status
   tail -f logs/*.log
   ```

## 📞 获取帮助

- 📖 **完整文档**: 查看 `DEPLOY_V2.md`
- 🔍 **状态检查**: 运行 `./deploy.sh --status`  
- 📋 **帮助信息**: 运行 `./deploy.sh --help`
- 🏥 **健康检查**: 访问 `/health/detailed/`

## 🎉 部署成功！

当你看到以下信息时，恭喜部署成功：

```
🎉 QAToolBox 部署完成！
🌐 网站地址: http://localhost:8000
👤 管理后台: http://localhost:8000/admin/
📋 用户名: admin
🔑 密码: admin123
```

现在你可以：
- 🌐 访问网站体验各种工具
- 👤 登录管理后台进行配置
- 🔧 根据需要配置API密钥
- 📊 查看应用状态和日志
