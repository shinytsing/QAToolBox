# QAToolBox 环境配置指南

## 🎯 环境分离策略

QAToolBox现在支持三种环境配置，满足不同场景的需求：

### 1. 测试环境 (Testing)
- **用途**: 本地开发和测试
- **数据库**: SQLite (db_test.sqlite3)
- **端口**: 8001
- **调试**: 开启
- **静态文件**: 开发模式
- **缓存**: 内存缓存

### 2. 生产环境 (Production)
- **用途**: 本地生产环境测试
- **数据库**: PostgreSQL
- **端口**: 8000
- **调试**: 关闭
- **静态文件**: 生产模式
- **缓存**: 内存缓存

### 3. 阿里云环境 (Aliyun)
- **用途**: 阿里云服务器部署
- **数据库**: PostgreSQL
- **缓存**: Redis
- **端口**: 8000
- **调试**: 关闭
- **静态文件**: 生产模式
- **日志**: /var/log/qatoolbox/

## 🚀 快速启动

### 环境切换
```bash
# 切换到测试环境
./switch_env.sh testing

# 切换到生产环境
./switch_env.sh production

# 切换到阿里云环境
./switch_env.sh aliyun
```

### 启动服务

#### 测试环境
```bash
python start_testing.py
# 访问: http://127.0.0.1:8001
```

#### 生产环境
```bash
python start_public_server.py
# 访问: http://localhost:8000
```

#### 阿里云环境
```bash
python start_aliyun.py
# 访问: http://localhost:8000
```

## 📁 文件结构

```
config/settings/
├── base.py              # 基础配置
├── development.py       # 开发环境配置
├── production.py        # 生产环境配置
├── testing.py          # 测试环境配置
└── aliyun_production.py # 阿里云环境配置

启动脚本:
├── start_testing.py     # 测试环境启动
├── start_public_server.py # 生产环境启动
└── start_aliyun.py     # 阿里云环境启动

部署脚本:
├── switch_env.sh       # 环境切换脚本
└── deploy_aliyun.sh    # 阿里云部署脚本
```

## 🔧 配置说明

### 数据库配置
- **测试环境**: SQLite，简化本地开发
- **生产环境**: PostgreSQL，支持高并发
- **阿里云环境**: PostgreSQL + Redis，企业级部署

### 静态文件配置
- **开发/测试**: 自动服务，支持热重载
- **生产/阿里云**: 收集到staticfiles目录，使用ManifestStaticFilesStorage

### 媒体文件配置
- **开发环境**: 直接服务，无需登录
- **生产环境**: 公共访问，无需登录
- **安全文件**: 需要登录验证（chat_images, avatars等）

### 日志配置
- **测试环境**: 控制台 + 文件日志
- **生产环境**: 文件日志，WARNING级别
- **阿里云环境**: 轮转日志，INFO级别

## 🌐 部署到阿里云

### 1. 准备服务器
```bash
# 安装依赖
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql redis-server nginx

# 创建项目目录
sudo mkdir -p /var/www/qatoolbox
sudo chown $USER:$USER /var/www/qatoolbox
```

### 2. 部署应用
```bash
# 上传代码到服务器
scp -r . user@server:/var/www/qatoolbox/

# 在服务器上运行部署脚本
cd /var/www/qatoolbox
./deploy_aliyun.sh
```

### 3. 配置域名
```bash
# 配置DNS解析
# shenyiqing.xin -> 服务器IP
# www.shenyiqing.xin -> 服务器IP
# app.shenyiqing.xin -> 服务器IP
```

## 🔍 故障排除

### 媒体文件404
- 检查MEDIA_ROOT配置
- 确认文件权限
- 验证URL配置

### 静态文件404
- 运行collectstatic命令
- 检查STATIC_ROOT配置
- 验证Nginx配置

### 数据库连接失败
- 检查数据库服务状态
- 验证连接参数
- 确认数据库用户权限

### 服务启动失败
- 查看日志: `sudo journalctl -u qatoolbox -f`
- 检查端口占用: `netstat -tlnp | grep :8000`
- 验证配置文件语法

## 📞 支持

如有问题，请检查：
1. 日志文件
2. 服务状态
3. 配置文件
4. 网络连接

---

**注意**: 生产环境部署前请确保：
- 修改默认密码
- 配置SSL证书
- 设置防火墙规则
- 备份数据库
