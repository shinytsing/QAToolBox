# 🌿 QAToolBox 分支策略和CI/CD流程

## 📋 分支策略概述

我们采用标准的 **GitFlow** 分支策略，明确区分开发和生产环境，确保代码质量和部署安全。

### 🎯 核心分支

#### 1. `main` 分支 (生产分支)
- **用途**: 生产环境代码
- **保护**: 🔒 受保护，只能通过PR合并
- **部署**: 自动触发 **CD - 持续部署** 到生产环境
- **质量要求**: 必须通过完整的CI流程

#### 2. `develop` 分支 (开发分支)
- **用途**: 开发环境集成
- **部署**: 自动触发部署到暂存环境
- **质量要求**: 必须通过CI测试

### 🚀 支持分支

#### 3. `feature/*` 分支 (功能分支)
- **用途**: 新功能开发
- **命名**: `feature/功能名称` (如: `feature/user-auth`)
- **合并**: 通过PR合并到 `develop`
- **生命周期**: 功能完成后删除

#### 4. `hotfix/*` 分支 (热修复分支)
- **用途**: 紧急生产问题修复
- **命名**: `hotfix/问题描述` (如: `hotfix/login-bug`)
- **合并**: 同时合并到 `main` 和 `develop`
- **生命周期**: 修复完成后删除

#### 5. `release/*` 分支 (发布分支)
- **用途**: 发布前的最终测试和微调
- **命名**: `release/版本号` (如: `release/v1.2.0`)
- **合并**: 测试完成后合并到 `main` 和 `develop`

## 🔄 CI/CD 流程详解

### CI - 持续集成 (Continuous Integration)

**触发条件**: 
- 推送到 `develop`、`feature/*`、`hotfix/*` 分支
- 向 `develop` 或 `main` 提交 Pull Request

**流程阶段**:
1. **代码质量检查** ⭐
   - 代码格式化验证 (Black, isort)
   - 静态代码分析 (Flake8, MyPy, Pylint)
   - 安全漏洞扫描 (Bandit, Safety)
   - 质量门禁: ≥70分

2. **单元测试** ⭐
   - 完整的单元测试套件
   - 测试覆盖率检查
   - 覆盖率门禁: ≥80%

3. **集成测试** ⭐
   - API集成测试
   - 端到端测试

4. **构建制品** ⭐
   - Docker镜像构建
   - 推送到容器注册表
   - 生成软件物料清单 (SBOM)

**结果**: 
- ✅ **成功**: 代码可以合并
- ❌ **失败**: 阻止合并，需要修复
- 📧 **通知**: 发送详细CI报告到 1009383129@qq.com

### CD - 持续交付 (Continuous Delivery)

**触发条件**: 手动触发，用于受控部署

**特点**:
- 🎯 **手动触发**: 需要人工决策何时部署
- 🔍 **多环境支持**: staging / production
- ✅ **部署审批**: 生产环境需要审批
- 📦 **一键部署**: 通过GitHub Actions界面

**流程阶段**:
1. **部署前检查**
   - 验证镜像存在
   - 环境配置检查
   - 安全策略验证

2. **环境部署**
   - 暂存环境: 自动部署和测试
   - 生产环境: 需要审批，创建备份

3. **部署后验证**
   - 健康检查
   - 功能验证
   - 性能测试

### CD - 持续部署 (Continuous Deployment)

**触发条件**: 
- 推送到 `main` 分支 (自动)
- 手动强制部署 (紧急情况)

**特点**:
- ⚡ **全自动**: 无需人工干预
- 🔍 **CI依赖**: 必须先通过完整CI
- 🛡️ **零停机**: 滚动更新部署
- 🔄 **自动回滚**: 检测到问题自动回滚

**流程阶段**:
1. **CI状态检查**
   - 等待CI完成
   - 验证CI通过

2. **自动部署**
   - 创建自动备份
   - 零停机滚动更新
   - 立即验证

3. **全面测试**
   - 部署后验证
   - 性能回归测试
   - 功能冒烟测试

4. **监控和回滚**
   - 自动监控设置
   - 问题检测和自动回滚

## 🔄 标准工作流程

### 功能开发流程

```bash
# 1. 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发和提交
git add .
git commit -m "feat: 实现新功能"
git push origin feature/new-feature

# 3. 创建PR到develop
# 4. CI自动运行 (代码质量 + 测试)
# 5. 代码审查和合并
# 6. 功能分支删除
```

### 发布流程

```bash
# 1. 从develop创建发布分支
git checkout develop
git checkout -b release/v1.2.0

# 2. 发布前准备
# - 更新版本号
# - 最终测试
# - 文档更新

# 3. 合并到main
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags

# 4. 自动触发CD - 持续部署
# 5. 合并回develop
git checkout develop
git merge release/v1.2.0
```

### 热修复流程

```bash
# 1. 从main创建热修复分支
git checkout main
git checkout -b hotfix/critical-bug

# 2. 快速修复
git add .
git commit -m "fix: 修复关键bug"

# 3. 合并到main (触发自动部署)
git checkout main
git merge hotfix/critical-bug
git push origin main

# 4. 合并到develop
git checkout develop
git merge hotfix/critical-bug
git push origin develop
```

## 📊 环境对应关系

| 环境 | 分支 | 部署方式 | URL | 用途 |
|------|------|----------|-----|------|
| **开发环境** | `develop` | 自动部署 | http://dev.shenyiqing.xin | 功能集成测试 |
| **暂存环境** | 手动选择 | CD-交付 | http://staging.shenyiqing.xin | 发布前验证 |
| **生产环境** | `main` | CD-部署 | http://shenyiqing.xin | 正式服务 |

## 📧 邮件通知规则

### CI通知 (每次代码提交)
- **收件人**: 1009383129@qq.com
- **内容**: 代码质量评分、测试覆盖率、构建状态
- **频率**: 每次CI运行

### CD通知 (部署时)
- **收件人**: 1009383129@qq.com
- **内容**: 部署状态、环境信息、访问链接
- **频率**: 每次部署操作

### 自动部署通知
- **收件人**: 1009383129@qq.com
- **内容**: 完整部署报告、监控信息、回滚状态
- **频率**: 每次自动部署

## ⚙️ 质量门禁标准

### CI质量要求
- ✅ **代码质量**: ≥70分
- ✅ **测试覆盖率**: ≥80%
- ✅ **安全扫描**: 无高危漏洞
- ✅ **格式检查**: 通过Black和isort

### 分支保护规则
- 🔒 `main` 分支: 需要PR审查 + CI通过
- 🔒 `develop` 分支: 需要CI通过
- ✅ 自动删除已合并的功能分支

## 🚀 快速开始

### 配置GitHub Secrets
```bash
# 服务器连接
SERVER_HOST=47.103.143.152
SERVER_USER=deploy
SERVER_SSH_KEY=<SSH私钥>

# 邮件通知
EMAIL_USERNAME=<Gmail账号>
EMAIL_PASSWORD=<Gmail应用专用密码>

# API密钥
DEEPSEEK_API_KEY=<API密钥>
# ... 其他API密钥
```

### 创建开发分支
```bash
git checkout -b develop
git push origin develop
```

### 第一次部署
```bash
# 推送到main分支触发自动部署
git checkout main
git push origin main
```

---

**这个分支策略确保了代码质量、部署安全和开发效率的完美平衡！** 🎯
