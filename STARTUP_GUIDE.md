# 🚀 商业化翻墙服务系统启动指南

## 📋 系统架构

这个翻墙服务系统包含两个核心组件：

1. **本地代理服务器** (端口8080) - 提供基础的HTTP代理服务
2. **Django Web服务** (端口8001) - 提供Web翻墙浏览器界面

## 🎯 快速启动

### 方法1: 一键启动脚本（推荐）

```bash
# 给脚本添加执行权限（首次使用）
chmod +x start_proxy_service.sh

# 启动完整服务
./start_proxy_service.sh
```

这个脚本会自动：
- ✅ 激活虚拟环境
- ✅ 安装必要依赖
- ✅ 启动本地代理服务器
- ✅ 启动Django Web服务

### 方法2: 手动启动

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 安装依赖
pip install requests PyYAML

# 3. 启动本地代理服务器（新终端）
python local_proxy_server.py

# 4. 启动Django服务（另一个新终端）
python manage.py runserver 8001
```

## 🌐 访问地址

- **主服务**: http://localhost:8001/tools/proxy-dashboard/
- **本地代理**: http://127.0.0.1:8080

## 🧪 测试系统

### 测试代理连接
```bash
python test_proxy_connection.py
```

### 测试Web翻墙功能
1. 打开 http://localhost:8001/tools/proxy-dashboard/
2. 登录系统
3. 点击YouTube、Google等快捷按钮
4. 或输入网址测试

## 🔧 故障排除

### 问题1: 端口被占用
```bash
# 查看端口占用
lsof -i :8001
lsof -i :8080

# 杀死占用进程
kill -9 <PID>
```

### 问题2: 本地代理启动失败
```bash
# 检查Python环境
python --version

# 检查依赖
pip list | grep requests
pip list | grep PyYAML

# 手动启动代理服务器
python local_proxy_server.py
```

### 问题3: Django服务启动失败
```bash
# 检查Django版本
python -c "import django; print(django.get_version())"

# 检查数据库迁移
python manage.py migrate

# 检查静态文件
python manage.py collectstatic
```

## 📊 系统状态监控

启动后，系统会显示：

- **本地IP**: 您的真实IP地址
- **代理IP**: 翻墙后的IP地址  
- **代理状态**: 本地代理服务器运行状态
- **系统状态**: 整体服务运行状态

## 🎉 成功标志

当看到以下信息时，说明系统启动成功：

```
🚀 本地代理服务器已启动: http://127.0.0.1:8080
✅ 本地代理服务器运行正常 (端口8080)
🌍 启动Django Web服务器...
💡 访问地址: http://localhost:8001/tools/proxy-dashboard/
🔧 本地代理: http://127.0.0.1:8080
```

## 💡 使用建议

1. **首次使用**: 建议使用一键启动脚本
2. **开发调试**: 可以分别启动两个服务
3. **生产部署**: 建议使用gunicorn等生产级WSGI服务器
4. **代理优化**: 可以配置更多公共代理节点

## 🔒 安全注意事项

- 本地代理服务器仅用于开发和测试
- 生产环境请使用专业的代理服务
- 定期更新依赖包以修复安全漏洞
- 监控系统日志，及时发现异常访问

## 📞 技术支持

如果遇到问题：

1. 检查终端错误信息
2. 运行测试脚本诊断
3. 查看Django日志文件
4. 确认网络连接正常

---

**🎯 现在您可以享受专业的Web翻墙服务了！**
