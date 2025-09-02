# 内网穿透解决方案

## 🚨 问题确认

您的ISP（互联网服务提供商）**全面阻止了所有端口的外网访问**，包括：
- ❌ 8000端口（被阻止）
- ❌ 8080端口（被阻止）  
- ❌ 80端口（被阻止）
- ❌ 9000端口（被阻止）
- ❌ 3000端口（被阻止）

## 🛠️ 解决方案

### 方案1：ngrok（需要注册）

#### 步骤1：注册ngrok账号
1. 访问：https://dashboard.ngrok.com/signup
2. 注册免费账号
3. 获取authtoken

#### 步骤2：配置ngrok
```bash
# 添加authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN

# 启动隧道
ngrok http 8000
```

#### 步骤3：获取公网地址
ngrok会显示类似这样的地址：
```
https://abc123.ngrok.io -> http://localhost:8000
```

### 方案2：Cloudflare Tunnel（推荐）

#### 步骤1：安装cloudflared
```bash
brew install cloudflared
```

#### 步骤2：登录Cloudflare
```bash
cloudflared tunnel login
```

#### 步骤3：创建隧道
```bash
# 创建隧道
cloudflared tunnel create qatoolbox

# 启动隧道
cloudflared tunnel --url http://localhost:8000
```

### 方案3：frp（开源免费）

#### 步骤1：下载frp
```bash
# 下载frp客户端
wget https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_darwin_arm64.tar.gz
tar -xzf frp_0.52.3_darwin_arm64.tar.gz
cd frp_0.52.3_darwin_arm64
```

#### 步骤2：配置frp
创建 `frpc.ini` 文件：
```ini
[common]
server_addr = 0.0.0.0
server_port = 7000

[web]
type = http
local_port = 8000
custom_domains = your-domain.com
```

#### 步骤3：启动frp
```bash
./frpc -c frpc.ini
```

### 方案4：natapp（国内服务）

#### 步骤1：注册natapp
1. 访问：https://natapp.cn/
2. 注册账号
3. 获取authtoken

#### 步骤2：下载客户端
```bash
# 下载natapp客户端
wget https://cdn.natapp.cn/assets/downloads/clients/2_3_9/natapp_darwin_arm64.zip
unzip natapp_darwin_arm64.zip
```

#### 步骤3：启动natapp
```bash
./natapp -authtoken=YOUR_AUTHTOKEN
```

### 方案5：使用云服务器（最稳定）

#### 推荐云服务商
- **阿里云ECS**：https://www.aliyun.com/product/ecs
- **腾讯云CVM**：https://cloud.tencent.com/product/cvm
- **华为云ECS**：https://www.huaweicloud.com/product/ecs.html
- **AWS EC2**：https://aws.amazon.com/ec2/

#### 部署步骤
1. 购买云服务器（最低配置即可）
2. 上传项目代码
3. 配置域名解析
4. 部署Django应用

## 🎯 立即可用方案

### 使用ngrok（最简单）

1. **注册ngrok账号**：
   - 访问：https://dashboard.ngrok.com/signup
   - 使用邮箱注册
   - 获取authtoken

2. **配置ngrok**：
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

3. **启动隧道**：
   ```bash
   ngrok http 8000
   ```

4. **获取公网地址**：
   ngrok会显示类似：`https://abc123.ngrok.io`

### 使用Cloudflare Tunnel（免费且稳定）

1. **安装cloudflared**：
   ```bash
   brew install cloudflared
   ```

2. **登录Cloudflare**：
   ```bash
   cloudflared tunnel login
   ```

3. **启动隧道**：
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```

## 📋 当前状态

- ✅ Django服务运行正常（8000端口）
- ✅ 本地访问正常
- ✅ 内网访问正常
- ❌ 外网访问被ISP阻止
- ✅ 内网穿透工具已准备就绪

## 🚀 下一步行动

1. **立即**：选择一种内网穿透方案
2. **推荐**：使用ngrok或Cloudflare Tunnel
3. **长期**：考虑使用云服务器

## ⚠️ 注意事项

- ISP端口阻止是常见现象
- 内网穿透是临时解决方案
- 云服务器是最稳定的长期方案
- 某些内网穿透服务有流量限制

## 📞 需要帮助？

如果您需要我帮您配置任何一种方案，请告诉我您的选择！
