# QAToolBox 部署命令

## 🚀 阿里云一键部署命令

### 方法1：快速修复部署（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/quick-fix-deploy.sh | bash
```

### 方法2：完整部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy-aliyun.sh | bash
```

### 方法3：分步执行
```bash
# 1. 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox

# 2. 配置环境变量
cp .env.production .env
nano .env  # 编辑配置你的API密钥

# 3. 执行快速修复部署
./quick-fix-deploy.sh
```

## 🔧 修复的问题

✅ **CORS跨域问题** - 配置允许所有来源
✅ **HTTPS重定向问题** - 禁用强制HTTPS重定向
✅ **API路由404错误** - 修复用户API路由配置
✅ **验证码500错误** - 简化验证码服务
✅ **登录页面路由问题** - 修复登录相关路由
✅ **Nginx HTTPS配置** - 支持SSL证书和HTTPS

## 🌐 访问地址

- **IP访问**: http://47.103.143.152
- **域名访问**: http://shenyiqing.xin
- **HTTPS访问**: https://shenyiqing.xin
- **管理员账号**: admin / admin123

## 📋 管理命令

- **监控服务**: `./monitor.sh`
- **备份数据**: `./backup.sh`
- **查看日志**: `docker-compose logs -f web`
- **重启服务**: `docker-compose restart`
- **停止服务**: `docker-compose down`

## 🔍 故障排除

如果遇到问题，可以运行：
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs web

# 重启服务
docker-compose restart

# 完全重新部署
docker-compose down && ./quick-fix-deploy.sh
```
