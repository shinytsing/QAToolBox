# GitHub Secrets 配置说明

为了让GitHub Actions自动部署到阿里云服务器，需要在GitHub仓库中配置以下Secrets：

## 配置步骤

1. 进入GitHub仓库页面
2. 点击 `Settings` 标签
3. 在左侧菜单中找到 `Secrets and variables` -> `Actions`
4. 点击 `New repository secret` 添加以下secrets：

## 必需的Secrets

### SERVER_HOST
- **值**: `47.103.143.152`
- **说明**: 阿里云服务器IP地址

### SERVER_USER
- **值**: `root` 或你的用户名
- **说明**: 服务器登录用户名

### SERVER_SSH_KEY
- **值**: 你的SSH私钥内容
- **说明**: 用于SSH连接服务器的私钥

### SERVER_PORT (可选)
- **值**: `22`
- **说明**: SSH端口，默认为22

## 如何获取SSH私钥

1. 在本地生成SSH密钥对（如果还没有）：
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

2. 将公钥添加到阿里云服务器：
```bash
# 复制公钥到服务器
ssh-copy-id -i ~/.ssh/id_rsa.pub root@47.103.143.152

# 或者手动添加
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

3. 将私钥内容复制到GitHub Secrets：
```bash
cat ~/.ssh/id_rsa
```

## 测试连接

配置完成后，可以手动触发工作流来测试：

1. 进入GitHub仓库的 `Actions` 标签
2. 选择 `Auto Deploy to Aliyun Server` 工作流
3. 点击 `Run workflow` 按钮
4. 查看运行日志确认部署是否成功

## 注意事项

- 确保服务器防火墙允许SSH连接
- 确保GitHub Actions有权限访问仓库
- 私钥内容要完整，包括 `-----BEGIN` 和 `-----END` 行
- 建议定期更新SSH密钥以提高安全性
