# 企业级CI/CD GitHub Secrets配置

为了让企业级CI/CD流程正常工作，需要在GitHub仓库中配置以下Secrets。

## 🔐 必需的GitHub Secrets

### 服务器连接配置
```
SERVER_HOST=47.103.143.152
SERVER_USER=root
SERVER_SSH_KEY=<你的SSH私钥内容>
SERVER_PORT=22
```

### 暂存环境配置（可选）
```
STAGING_HOST=<暂存服务器IP>
STAGING_USER=<暂存服务器用户名>
STAGING_SSH_KEY=<暂存服务器SSH私钥>
STAGING_PORT=22
```

### 邮件通知配置
```
EMAIL_USERNAME=<发送邮件的Gmail账号>
EMAIL_PASSWORD=<Gmail应用专用密码>
```

## 📧 邮件配置说明

### 1. 创建Gmail应用专用密码

1. 登录你的Gmail账号
2. 进入 [Google账号管理](https://myaccount.google.com/)
3. 点击"安全性" → "两步验证"（需要先启用）
4. 点击"应用专用密码"
5. 选择"自定义名称"，输入"QAToolBox CI/CD"
6. 生成16位应用专用密码
7. 将此密码作为 `EMAIL_PASSWORD` 的值

### 2. 推荐的发送邮箱配置

为了专业性，建议创建专门的CI/CD邮箱：
- 邮箱示例：`qatoolbox-cicd@gmail.com`
- 或使用现有邮箱的别名

## 🔑 SSH密钥配置

### 生成新的SSH密钥对
```bash
# 为部署专用生成SSH密钥
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qatoolbox_deploy -C "qatoolbox-deploy"

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/qatoolbox_deploy.pub root@47.103.143.152

# 复制私钥内容到GitHub Secrets
cat ~/.ssh/qatoolbox_deploy
```

### 服务器安全配置
```bash
# 在服务器上创建专用部署用户（推荐）
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo mkdir -p /home/deploy/.ssh
sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys

# 给deploy用户sudo权限（仅限必要命令）
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/docker" | sudo tee /etc/sudoers.d/deploy
```

## 🚀 GitHub环境配置

### 设置环境保护规则

1. 进入仓库 Settings → Environments
2. 创建 `production` 环境
3. 配置保护规则：
   - Required reviewers: 至少1个审核者
   - Wait timer: 0分钟（或根据需求设置）
   - Deployment branches: 仅限main分支

### 配置Secrets步骤

1. 进入 GitHub 仓库页面
2. 点击 `Settings` 标签
3. 在左侧菜单中找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 添加上述secrets

## 📊 需要的个人数据清单

为了完成企业级CI/CD配置，我需要你提供以下信息：

### ✅ 已知信息
- 生产服务器IP: `47.103.143.152`
- 域名: `shenyiqing.xin`
- 通知邮箱: `1009383129@qq.com`

### ❓ 需要确认的信息

1. **服务器登录信息**
   - SSH用户名（建议：deploy）
   - SSH端口（默认：22）
   - 项目部署路径（默认：~/QAToolBox）

2. **邮件发送配置**
   - 发送邮件的Gmail账号
   - Gmail应用专用密码

3. **环境配置**
   - 是否需要暂存环境？
   - 是否需要部署审批流程？
   - 代码覆盖率要求（默认：80%）

4. **通知偏好**
   - 除了邮件，是否需要其他通知方式（Slack、钉钉等）？
   - 通知频率（每次部署 vs 仅失败时）

## 🔍 测试配置

配置完成后，测试步骤：

1. 手动触发工作流验证
2. 检查邮件通知是否正常
3. 验证部署流程是否正确
4. 确认所有质量门禁是否工作

## 📞 支持联系

如需帮助配置，请提供：
- 服务器访问权限
- GitHub仓库管理员权限
- 邮箱配置权限
