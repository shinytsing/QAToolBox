# QAToolBox 部署和测试指南

## 📋 概述

本指南提供了QAToolBox项目的完整部署和测试解决方案，包括：

- ✅ 一键部署脚本
- 🧪 全面的自动化测试框架
- 📱 移动端优化
- 📊 系统监控和健康检查
- 🚀 生产环境配置

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd QAToolBox

# 复制环境配置
cp env.example .env
# 编辑 .env 文件，配置数据库、Redis等
```

### 2. 一键部署

```bash
# 开发环境部署
./scripts/one_click_deploy.sh development

# 生产环境部署
./scripts/one_click_deploy.sh production --skip-tests

# Docker部署
./scripts/one_click_deploy.sh production --docker
```

## 🧪 测试框架

### 测试类型

1. **单元测试** - 测试单个组件功能
2. **集成测试** - 测试组件间集成
3. **API测试** - 测试REST API接口
4. **端到端测试** - 测试完整用户流程
5. **性能测试** - 测试系统性能和负载
6. **安全测试** - 测试安全漏洞和防护

### 运行测试

```bash
# 运行所有测试
./scripts/run_tests.sh

# 运行特定类型测试
./scripts/run_tests.sh unit           # 单元测试
./scripts/run_tests.sh integration   # 集成测试
./scripts/run_tests.sh api           # API测试
./scripts/run_tests.sh e2e           # 端到端测试
./scripts/run_tests.sh performance   # 性能测试

# 运行冒烟测试
./scripts/run_tests.sh --smoke

# 详细输出
./scripts/run_tests.sh unit --verbose

# 快速失败模式
./scripts/run_tests.sh --fail-fast
```

### 测试配置

测试配置文件位于：
- `tests/conftest.py` - pytest配置和夹具
- `pytest.ini` - pytest设置
- `requirements/testing.txt` - 测试依赖

### 覆盖率报告

测试完成后，覆盖率报告位于：
- `htmlcov/index.html` - HTML格式覆盖率报告
- `test_reports/` - 各种测试报告

## 📱 移动端优化

### 响应式设计

项目包含完整的移动端优化：

1. **CSS优化** (`src/static/css/mobile.css`)
   - 响应式布局
   - 触摸友好的界面
   - 移动端导航
   - 深色模式支持

2. **JavaScript优化** (`src/static/js/mobile.js`)
   - 触摸事件处理
   - 移动端交互
   - 性能优化
   - 离线支持

### 移动端测试

```bash
# 移动端兼容性测试
./scripts/run_tests.sh e2e --browser mobile

# 性能测试（移动端）
./scripts/run_tests.sh performance --mobile
```

## 📊 监控和健康检查

### 健康检查

```bash
# 系统健康检查
python monitoring/health_check.py

# JSON格式输出
python monitoring/health_check.py --json

# 保存报告
python monitoring/health_check.py --output health_report.json
```

### 实时监控仪表板

```bash
# 启动监控仪表板
python scripts/monitoring_dashboard.py

# 自定义刷新间隔
python scripts/monitoring_dashboard.py --interval 5

# 启用告警
python scripts/monitoring_dashboard.py --alerts

# 保存监控数据
python scripts/monitoring_dashboard.py --save metrics.json
```

### 监控指标

监控系统跟踪以下指标：

1. **系统指标**
   - CPU使用率和负载
   - 内存使用情况
   - 磁盘空间使用
   - 网络流量
   - 进程数量

2. **应用指标**
   - Web服务器状态
   - 数据库连接
   - Redis缓存状态
   - Celery任务队列
   - 外部API连接

3. **性能指标**
   - 响应时间
   - 吞吐量
   - 错误率
   - 资源使用趋势

## 🏗️ 部署架构

### 开发环境

```
应用服务器 (Django) + SQLite + Redis + Celery
```

### 生产环境

```
负载均衡器 (Nginx) 
    ↓
应用服务器 (Gunicorn + Django)
    ↓
数据库 (PostgreSQL) + 缓存 (Redis) + 任务队列 (Celery)
    ↓
监控系统 (Prometheus + Grafana)
```

### Docker部署

使用 `docker-compose.prod.yml` 进行容器化部署：

```bash
# 构建和启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🔧 配置说明

### 环境变量

主要环境变量配置：

```bash
# Django配置
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com

# 数据库配置
DB_NAME=qatoolbox
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/1

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 生产环境优化

1. **性能优化**
   - 启用Gzip压缩
   - 静态文件CDN
   - 数据库连接池
   - Redis缓存优化

2. **安全配置**
   - HTTPS强制重定向
   - 安全头设置
   - CSRF保护
   - SQL注入防护

3. **监控配置**
   - 错误日志收集
   - 性能指标监控
   - 健康检查端点
   - 告警通知

## 📝 CI/CD 集成

### GitHub Actions 示例

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements/testing.txt
    - name: Run tests
      run: |
        ./scripts/run_tests.sh --no-coverage
    - name: Run security scan
      run: |
        ./scripts/run_tests.sh security

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        ./scripts/one_click_deploy.sh production
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库状态
   python monitoring/health_check.py
   
   # 重置数据库连接
   python manage.py dbshell
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis状态
   redis-cli ping
   
   # 重启Redis服务
   sudo systemctl restart redis
   ```

3. **静态文件404**
   ```bash
   # 重新收集静态文件
   python manage.py collectstatic --noinput
   ```

4. **Celery任务失败**
   ```bash
   # 查看Celery状态
   celery -A QAToolBox inspect active
   
   # 重启Celery工作进程
   pkill -f celery
   celery -A QAToolBox worker -D
   ```

### 日志文件

关键日志文件位置：
- `logs/django.log` - Django应用日志
- `logs/access.log` - 访问日志
- `logs/error.log` - 错误日志
- `alerts.log` - 告警日志

## 📚 最佳实践

### 部署前检查清单

- [ ] 环境变量配置完整
- [ ] 数据库迁移执行完成
- [ ] 静态文件收集完成
- [ ] SSL证书配置正确
- [ ] 监控系统运行正常
- [ ] 备份策略已实施
- [ ] 回滚计划已准备

### 测试策略

1. **开发阶段**
   - 编写单元测试
   - 本地运行集成测试
   - 代码覆盖率 > 80%

2. **测试环境**
   - 完整的自动化测试
   - 性能基准测试
   - 安全扫描

3. **生产环境**
   - 冒烟测试
   - 健康检查
   - 监控告警

### 性能优化

1. **数据库优化**
   - 添加适当索引
   - 查询优化
   - 连接池配置

2. **缓存策略**
   - Redis缓存热点数据
   - CDN静态资源
   - 浏览器缓存

3. **代码优化**
   - 异步任务处理
   - 数据库查询优化
   - 静态文件压缩

## 🔗 相关链接

- [Django官方文档](https://docs.djangoproject.com/)
- [pytest文档](https://docs.pytest.org/)
- [Docker文档](https://docs.docker.com/)
- [Nginx配置指南](https://nginx.org/en/docs/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)

## 📞 支持

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查日志文件
3. 运行健康检查脚本
4. 提交Issue到项目仓库

---

🎉 **恭喜！** 您的QAToolBox项目现在已经具备了完整的企业级部署和测试能力！
