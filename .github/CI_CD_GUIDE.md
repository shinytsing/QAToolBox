# QAToolBox 统一CI/CD系统指南

## 🚀 概述

QAToolBox现在使用统一的CI/CD系统，替代了之前7个独立的workflow文件。新系统保持了所有原有功能，同时消除了配置冲突和资源浪费。

## 📋 功能特性

### 1. 统一工作流
- **单一入口**：所有CI/CD功能通过一个workflow文件管理
- **智能触发**：根据分支和事件类型自动选择执行流程
- **功能完整**：保留所有原有功能，无功能缩减

### 2. 支持的工作流类型

#### 自动触发
- **Push到main分支**：执行完整CI/CD流程，包括自动部署到生产环境
- **Push到develop分支**：执行CI流程，构建镜像但不部署
- **Push到feature/*分支**：执行CI流程，代码质量检查和测试
- **Pull Request**：执行CI流程，代码质量检查和测试

#### 手动触发
- **CI流程**：仅执行代码质量检查和测试
- **持续交付**：手动选择环境进行部署
- **持续部署**：自动部署到生产环境
- **紧急部署**：跳过所有检查的紧急部署

## 🔧 配置说明

### 环境变量
```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  NOTIFICATION_EMAIL: "1009383129@qq.com"
  PYTHON_VERSION: '3.12'
```

### 必需的Secrets
- `SERVER_HOST`: 生产服务器地址
- `SERVER_USER`: 生产服务器用户名
- `SERVER_SSH_KEY`: 生产服务器SSH密钥
- `SERVER_PORT`: 生产服务器端口（可选，默认22）
- `STAGING_HOST`: 暂存服务器地址
- `STAGING_USER`: 暂存服务器用户名
- `STAGING_SSH_KEY`: 暂存服务器SSH密钥
- `STAGING_PORT`: 暂存服务器端口（可选，默认22）
- `EMAIL_USERNAME`: 邮件通知用户名
- `EMAIL_PASSWORD`: 邮件通知密码

## 📊 质量门禁

### 代码质量检查
- **Black格式化检查**：代码格式必须符合Black标准
- **isort导入排序**：导入语句必须正确排序
- **Flake8代码检查**：静态代码分析
- **MyPy类型检查**：类型注解检查
- **Bandit安全扫描**：安全漏洞检测
- **Safety依赖扫描**：依赖包漏洞检测

### 测试要求
- **单元测试**：必须通过所有单元测试
- **集成测试**：API集成测试
- **测试覆盖率**：要求≥80%（严格标准）
- **数据库测试**：支持PostgreSQL和SQLite

## 🚀 部署流程

### 1. 持续集成（CI）
```mermaid
graph LR
    A[代码提交] --> B[代码质量检查]
    B --> C[单元测试]
    C --> D[集成测试]
    D --> E[构建Docker镜像]
    E --> F[推送镜像]
```

### 2. 持续部署（CD）
```mermaid
graph LR
    A[CI通过] --> B[创建备份]
    B --> C[零停机部署]
    C --> D[健康检查]
    D --> E[部署后验证]
    E --> F[发送通知]
```

## 🛠️ 使用方法

### 手动触发工作流
1. 进入GitHub Actions页面
2. 选择"QAToolBox Unified CI/CD Pipeline"
3. 点击"Run workflow"
4. 选择工作流类型：
   - **CI流程**：仅代码检查和测试
   - **持续交付**：手动选择环境部署
   - **持续部署**：自动部署到生产环境
   - **紧急部署**：跳过检查的紧急部署

### 分支策略
- **main分支**：生产环境，自动部署
- **develop分支**：开发环境，仅CI流程
- **feature/*分支**：功能分支，仅CI流程
- **hotfix/*分支**：热修复分支，仅CI流程

## 📈 监控和通知

### 邮件通知
- 每次工作流执行都会发送邮件通知
- 包含详细的执行状态和结果
- 支持HTML格式的详细报告

### 健康检查
- 自动检查应用健康状态
- 验证关键API端点
- 检查静态文件可访问性
- 监控响应时间

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务是否启动
   - 验证数据库连接配置
   - 确认环境变量设置正确

2. **测试失败**
   - 检查测试覆盖率是否达标
   - 验证测试环境配置
   - 查看详细测试日志

3. **部署失败**
   - 检查SSH连接配置
   - 验证服务器访问权限
   - 查看部署日志

### 调试模式
在workflow文件中添加以下环境变量启用调试：
```yaml
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

## 📚 相关文件

- `.github/workflows/unified-ci-cd.yml` - 统一CI/CD工作流
- `config/settings/testing.py` - 测试环境配置
- `scripts/post_deployment_verification.py` - 部署后验证脚本
- `requirements.txt` - 项目依赖

## 🎯 优化效果

### 解决的问题
1. ✅ 消除了7个workflow文件的配置冲突
2. ✅ 统一了数据库配置，支持PostgreSQL和SQLite
3. ✅ 优化了依赖管理，解决版本冲突
4. ✅ 减少了资源浪费，避免重复执行
5. ✅ 保持了所有原有功能，无功能缩减

### 预期效果
- 大幅减少workflow失败次数
- 提高CI/CD执行效率
- 简化维护和管理
- 保持系统功能完整性

## 📞 支持

如有问题或建议，请联系开发团队或提交Issue。
