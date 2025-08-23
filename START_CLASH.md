# 🚀 启动Clash客户端 - 翻墙系统使用指南

## 📋 前置要求

要使用翻墙系统，您需要先启动Clash客户端。根据您提供的配置文件，系统将使用以下端口：

- **HTTP代理**: 127.0.0.1:7890
- **SOCKS5代理**: 127.0.0.1:7891

## 🔧 启动Clash客户端

### 方法1: 使用Clash for Windows/Mac
1. 下载并安装Clash客户端
2. 将您的配置文件复制到Clash配置目录
3. 启动Clash客户端
4. 确保代理端口7890和7891已启用

### 方法2: 使用Clash Core
```bash
# 下载Clash核心
wget https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-darwin-amd64-v1.18.0.gz

# 解压
gunzip clash-darwin-amd64-v1.18.0.gz

# 给执行权限
chmod +x clash-darwin-amd64-v1.18.0

# 创建配置目录
mkdir -p ~/.config/clash

# 复制配置文件
cp your_clash_config.yaml ~/.config/clash/config.yaml

# 启动Clash
./clash-darwin-amd64-v1.18.0 -d ~/.config/clash/
```

### 方法3: 使用Docker
```bash
# 创建配置目录
mkdir -p ~/.config/clash

# 复制配置文件
cp your_clash_config.yaml ~/.config/clash/config.yaml

# 启动Clash容器
docker run -d \
  --name clash \
  -p 7890:7890 \
  -p 7891:7891 \
  -p 9090:9090 \
  -v ~/.config/clash:/root/.config/clash \
  dreamacro/clash:latest
```

## ✅ 验证Clash是否运行

### 检查端口状态
```bash
# 检查HTTP代理端口
lsof -i :7890

# 检查SOCKS5代理端口
lsof -i :7891

# 检查控制端口
lsof -i :9090
```

### 测试代理连接
```bash
# 测试HTTP代理
curl -x http://127.0.0.1:7890 http://httpbin.org/ip

# 测试SOCKS5代理
curl --socks5 127.0.0.1:7891 http://httpbin.org/ip
```

## 🌐 启动翻墙系统

### 1. 启动Django服务器
```bash
cd /Users/gaojie/PycharmProjects/QAToolBox
source .venv/bin/activate
python manage.py runserver 8001
```

### 2. 测试翻墙功能
```bash
# 运行Clash代理测试
python test_clash_proxy.py
```

### 3. 访问Web界面
打开浏览器访问: http://localhost:8001/tools/proxy-dashboard/

## 🔍 故障排除

### 问题1: 端口被占用
```bash
# 查看端口占用
lsof -i :7890
lsof -i :7891

# 杀死占用进程
kill -9 <PID>
```

### 问题2: Clash启动失败
1. 检查配置文件格式是否正确
2. 确认端口没有被其他程序占用
3. 查看Clash日志输出

### 问题3: 代理连接失败
1. 确认Clash正在运行
2. 检查防火墙设置
3. 验证代理节点是否可用

## 📱 使用说明

### 启动顺序
1. **第一步**: 启动Clash客户端
2. **第二步**: 启动Django服务器
3. **第三步**: 测试代理连接
4. **第四步**: 使用Web翻墙浏览器

### 验证步骤
1. 运行 `python test_clash_proxy.py`
2. 看到 "🎉 翻墙系统工作正常！" 表示成功
3. 访问Web界面使用翻墙功能

## 🎯 预期结果

启动成功后，您应该能够：
- ✅ 通过代理访问Google、YouTube等外网
- ✅ 在Web界面中使用翻墙浏览器
- ✅ 享受无障碍的全球网络访问

---

**💡 重要提示**: 请确保Clash客户端正在运行，否则翻墙系统无法工作！
