# SSL证书配置指南

## 当前状态
- ✅ HTTP访问正常: http://shenyiqing.xin/
- ❌ HTTPS访问失败: https://shenyiqing.xin/

## 解决方案

### 方案1: Cloudflare控制台配置（推荐）

1. **登录Cloudflare**
   - 访问: https://dash.cloudflare.com/
   - 添加域名: shenyiqing.xin

2. **DNS配置**
   ```
   类型: A
   名称: @
   内容: 192.0.2.1
   代理状态: 已代理 (橙色云朵)
   ```

3. **SSL/TLS设置**
   - 加密模式: "完全"
   - 始终使用HTTPS: 开启
   - 边缘证书: 自动

### 方案2: 使用Let's Encrypt

```bash
# 安装certbot
brew install certbot

# 获取证书
sudo certbot certonly --standalone -d shenyiqing.xin

# 配置nginx或apache使用证书
```

### 方案3: 使用Cloudflare Tunnel配置

创建配置文件 `~/.cloudflared/config.yml`:

```yaml
tunnel: shenyiqing-tunnel
credentials-file: /Users/gaojie/.cloudflared/shenyiqing-tunnel.json

ingress:
  - hostname: shenyiqing.xin
    service: http://localhost:8000
  - service: http_status:404
```

### 方案4: 临时解决方案

使用HTTP访问，配置反向代理：

```bash
# 使用nginx作为反向代理
sudo nginx -t
sudo systemctl reload nginx
```

## 当前可用地址

- **HTTP**: http://shenyiqing.xin/
- **API**: http://shenyiqing.xin/tools/api/generate-testcases/
- **工具**: http://shenyiqing.xin/tools/work/

## 注意事项

1. **域名所有权**: 确保您拥有 shenyiqing.xin 域名
2. **DNS设置**: 域名必须指向Cloudflare
3. **证书有效期**: Let's Encrypt证书90天需要续期
4. **防火墙**: 确保443端口开放

## 测试命令

```bash
# 测试HTTP
curl -I http://shenyiqing.xin/

# 测试HTTPS
curl -I https://shenyiqing.xin/

# 测试API
curl -X POST http://shenyiqing.xin/tools/api/generate-testcases/ \
  -H "Content-Type: application/json" \
  -d '{"requirement":"测试","prompt":"生成测试用例"}'
```
