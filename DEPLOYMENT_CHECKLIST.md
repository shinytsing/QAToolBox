# 🚀 QAToolBox 企业级部署清单

## 📋 部署前检查清单

### ✅ 代码准备
- [ ] 所有代码已提交并推送到main分支
- [ ] 代码已通过本地测试
- [ ] 版本标签已创建（可选）
- [ ] 变更日志已更新

### ✅ 服务器准备
- [ ] 服务器可访问 (47.103.143.152)
- [ ] Docker和Docker Compose已安装
- [ ] SSH密钥已配置
- [ ] 防火墙端口已开放 (80, 443, 22)
- [ ] 域名DNS已正确配置 (shenyiqing.xin)

### ✅ GitHub配置
- [ ] Repository secrets已配置完成
- [ ] Environments已设置（production）
- [ ] Workflow permissions已启用
- [ ] Branch protection rules已设置（可选）

### ✅ 环境变量配置
- [ ] .env.production文件已更新
- [ ] API密钥已配置
- [ ] 数据库密码已设置
- [ ] 邮件配置已完成

## 🔐 必需的GitHub Secrets

### 服务器连接
```bash
SERVER_HOST=47.103.143.152
SERVER_USER=root  # 或deploy用户
SERVER_SSH_KEY=<SSH私钥内容>
SERVER_PORT=22
```

### 邮件通知
```bash
EMAIL_USERNAME=<Gmail邮箱>
EMAIL_PASSWORD=<Gmail应用专用密码>
```

### 暂存环境（可选）
```bash
STAGING_HOST=<暂存服务器IP>
STAGING_USER=<暂存用户>
STAGING_SSH_KEY=<暂存SSH密钥>
```

## 📊 需要确认的个人信息

### 🔍 当前已知信息
- ✅ 生产服务器: 47.103.143.152
- ✅ 域名: shenyiqing.xin
- ✅ 通知邮箱: 1009383129@qq.com

### ❓ 需要提供的信息

1. **服务器访问信息**
   - SSH用户名 (推荐: deploy)
   - SSH私钥文件路径
   - 项目部署路径 (默认: ~/QAToolBox)

2. **邮件发送配置**
   - 发送邮件的Gmail账号
   - Gmail应用专用密码 (16位)

3. **部署配置**
   - 是否需要暂存环境？
   - 是否需要人工审批？
   - 代码覆盖率要求 (默认: 80%)

4. **API密钥**
   - DEEPSEEK_API_KEY
   - GOOGLE_API_KEY
   - GOOGLE_CSE_ID
   - OPENWEATHER_API_KEY

## 🚀 部署流程

### 自动部署
1. 推送代码到main分支
2. GitHub Actions自动触发
3. 自动运行测试和构建
4. 自动部署到生产环境
5. 发送邮件通知到 1009383129@qq.com

### 手动部署
1. 进入GitHub Actions
2. 选择"Enterprise CI/CD Pipeline"
3. 点击"Run workflow"
4. 选择环境和参数
5. 确认执行

## 📧 邮件通知内容

邮件将包含以下信息：
- 部署状态概览
- 各阶段执行结果
- 代码覆盖率
- 访问链接
- 错误详情（如有）

## ✅ 部署后验证

### 自动验证
- 健康检查 (/health/)
- 首页加载测试
- API端点测试
- 基础性能测试

### 手动验证
- [ ] 网站可正常访问: http://shenyiqing.xin
- [ ] IP访问正常: http://47.103.143.152
- [ ] 管理后台可访问: http://shenyiqing.xin/admin/
- [ ] 核心功能正常工作
- [ ] 邮件通知已收到

## 🔧 故障排除

### 常见问题
1. **SSH连接失败**
   ```bash
   # 检查SSH密钥格式
   ssh -i ~/.ssh/deploy_key root@47.103.143.152
   ```

2. **Docker构建失败**
   ```bash
   # 检查服务器磁盘空间
   df -h
   docker system prune -f
   ```

3. **邮件发送失败**
   - 检查Gmail应用专用密码
   - 确认两步验证已启用
   - 验证邮箱地址格式

### 回滚步骤
```bash
# 连接服务器
ssh root@47.103.143.152

# 回滚到上一个版本
cd ~/QAToolBox
git log --oneline -5
git checkout <上一个commit>
./quick-fix-deploy.sh
```

## 📞 支持联系

如需技术支持，请提供：
- GitHub Actions运行日志
- 服务器错误日志
- 具体错误信息
- 环境配置详情

---

**部署完成后，系统将自动发送详细的部署报告到 1009383129@qq.com**
