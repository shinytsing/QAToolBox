# QAToolBox 服务器启动指南

## 🎯 概述

QAToolBox 项目现在支持同时启动API服务和WebSocket聊天服务器，提供完整的实时通信功能。

## 🚀 启动方式

### 方式1: 统一启动脚本（推荐）

```bash
# 使用Python脚本启动
python start_unified_server.py

# 或使用Shell脚本启动
./start_server.sh
```

### 方式2: 快速启动

```bash
# 快速启动（简化版）
python quick_start.py
```

### 方式3: 原有启动脚本

```bash
# 使用项目启动脚本
python start_project.py
```

## 📍 服务地址

启动成功后，您可以访问以下地址：

- **🌐 主应用**: http://localhost:8000
- **🔌 WebSocket**: ws://localhost:8000/ws/
- **📱 API服务**: http://localhost:8001
- **💬 聊天功能**: http://localhost:8000/tools/chat/
- **❤️ 心动链接**: http://localhost:8000/tools/heart_link/
- **🎯 数字匹配**: http://localhost:8000/tools/number-match/

## ⚙️ 启动选项

### 统一启动脚本选项

```bash
# 基本启动
python start_unified_server.py

# 指定端口
python start_unified_server.py --port 8000 --api-port 8001

# 仅启动ASGI服务器（WebSocket）
python start_unified_server.py --asgi-only

# 仅启动API服务器
python start_unified_server.py --api-only

# 跳过某些步骤
python start_unified_server.py --no-redis --no-migrate --no-static
```

### Shell脚本选项

```bash
# 显示帮助
./start_server.sh --help

# 开发模式（跳过端口检查）
./start_server.sh --dev

# 指定端口
./start_server.sh --port 8000 --api-port 8001

# 仅启动特定服务
./start_server.sh --asgi-only
./start_server.sh --api-only
```

## 🔧 功能特性

### 统一启动脚本 (`start_unified_server.py`)

- ✅ 同时启动ASGI和Django服务器
- ✅ 自动检查依赖
- ✅ 自动运行数据库迁移
- ✅ 自动收集静态文件
- ✅ 自动检查Redis服务
- ✅ 优雅关闭所有服务
- ✅ 实时监控服务状态
- ✅ 支持自定义端口

### Shell启动脚本 (`start_server.sh`)

- ✅ 友好的彩色输出
- ✅ 环境检查（Python、虚拟环境）
- ✅ 依赖自动安装
- ✅ 端口占用检查
- ✅ 交互式确认
- ✅ 信号处理

## 🛠️ 故障排除

### 1. 端口被占用

```bash
# 检查端口占用
lsof -i :8000
lsof -i :8001

# 终止占用进程
kill -9 <PID>
```

### 2. 依赖缺失

```bash
# 安装依赖
pip install -r requirements/dev.txt
```

### 3. Redis未启动

```bash
# 启动Redis
redis-server

# 或跳过Redis检查
python start_unified_server.py --no-redis
```

### 4. 数据库迁移失败

```bash
# 手动运行迁移
python manage.py migrate

# 或跳过迁移
python start_unified_server.py --no-migrate
```

### 5. WebSocket连接失败

1. 确保使用ASGI服务器（端口8000）
2. 检查用户是否已登录
3. 访问聊天调试页面：http://localhost:8000/tools/chat/debug/test-room-123/

## 📋 服务说明

### ASGI服务器（端口8000）
- 支持WebSocket连接
- 处理实时聊天功能
- 支持HTTP请求
- 基于Daphne服务器

### Django开发服务器（端口8001）
- 处理API请求
- 提供RESTful接口
- 支持静态文件服务
- 开发调试功能

## 🔄 服务管理

### 启动服务
```bash
# 推荐方式
./start_server.sh

# 或
python start_unified_server.py
```

### 停止服务
```bash
# 按 Ctrl+C 优雅停止
# 或使用信号
kill -TERM <PID>
```

### 重启服务
```bash
# 停止后重新启动
./start_server.sh
```

## 📝 日志查看

启动脚本会显示实时日志：

```
[ASGI] 🚀 启动ASGI服务器 (支持WebSocket)...
[ASGI] 📍 服务器地址: http://localhost:8000
[Django] 🌐 启动Django开发服务器 (API服务)...
[Django] 📍 服务器地址: http://localhost:8001
```

## 🎉 成功启动标志

当看到以下信息时，表示服务启动成功：

```
✅ 数据库迁移完成
✅ 静态文件收集完成
✅ Redis服务器已运行
🚀 启动ASGI服务器 (支持WebSocket)...
🌐 启动Django开发服务器 (API服务)...
📍 ASGI服务器: http://localhost:8000
📍 API服务器: http://localhost:8001
🔌 WebSocket: ws://localhost:8000/ws/
```

## 🔗 相关文档

- [聊天室使用指南](CHAT_ROOM_USAGE_GUIDE.md)
- [WebSocket聊天功能增强总结](WEBSOCKET_CHAT_ENHANCEMENT_SUMMARY.md)
- [聊天室问题诊断](CHAT_ROOM_TROUBLESHOOTING.md)
