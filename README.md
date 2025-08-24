# QAToolBox - 智能工具箱

QAToolBox 是一个功能强大的Django工具箱项目，集成了AI工具、数据处理、图像识别等多种实用功能。

## 🚀 一键部署

```bash
# 克隆项目
git clone https://github.com/shinytsing/QAToolBox.git
cd QAToolBox

# 一键部署
./deploy.sh
```

支持三种部署方式：
- 🔧 本地开发环境
- 🚀 生产环境部署  
- 🐳 Docker容器化

详细部署说明请查看 [DEPLOY_V2.md](DEPLOY_V2.md)

## 🚀 功能特色

### 生活模式
- 📝 **生活日记** - 记录日常生活和心情
- ✍️ **爆款文案** - AI驱动的文案生成
- 🧘 **冥想指导** - 冥想练习和指导

### 极客模式
- 🕷️ **数据爬虫** - 网页数据抓取工具
- 📄 **PDF转换引擎** - PDF转Word等格式转换
- 🧪 **测试用例生成器** - 自动化测试用例生成

### 狂暴模式
- 💪 **锻炼中心** - 健身计划和记录

### Emo模式
- 🔍 **自我分析** - 个人情绪和行为分析
- 📖 **故事版生成** - 创意故事生成
- 🔮 **命运解析** - 趣味命运分析

## 🛠️ 技术栈

- **后端框架**: Django 4.2
- **API框架**: Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **缓存**: Redis
- **任务队列**: Celery
- **前端**: HTML/CSS/JavaScript + Bootstrap 5
- **部署**: Gunicorn + Nginx

## 📋 系统要求

- Python 3.8+
- pip
- 虚拟环境 (推荐)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd ModeShift
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements/dev.txt
```

### 4. 配置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，填入必要的配置
```

### 5. 初始化数据库
```bash
python setup_database.py
```

### 6. 启动开发服务器
```bash
python manage.py runserver
```

或者使用一键启动脚本：
```bash
python start_project.py
```

## 📁 项目结构

```
ModeShift/
├── apps/                    # 应用模块
│   ├── users/              # 用户系统
│   ├── content/            # 内容管理
│   └── tools/              # 工具模块
├── config/                 # 配置文件
│   └── settings/
│       ├── base.py         # 基础配置
│       ├── development.py  # 开发环境
│       └── production.py   # 生产环境
├── templates/              # 模板文件
├── src/static/             # 静态文件
├── media/                  # 媒体文件
├── requirements/           # 依赖文件
├── setup_database.py       # 数据库初始化
├── start_project.py        # 项目启动脚本
└── manage.py              # Django管理脚本
```

## 🗄️ 数据库设计

项目包含完整的数据库设计，涵盖：

### 用户系统
- 用户角色管理
- 会员系统
- 用户状态管理
- 活动日志追踪

### 工具系统
- 工具使用记录
- 社交媒体监控
- 生活管理功能

### 内容系统
- 文章管理
- 用户反馈
- 公告系统
- AI友情链接

详细设计请参考 [database_design.md](database_design.md)

## 🔧 开发指南

### 环境配置
- 开发环境：`config.settings.development`
- 生产环境：`config.settings.production`

### 代码规范
```bash
# 代码格式化
black .
isort .

# 代码检查
flake8 .
pylint apps/
```

### 测试
```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=apps/
```

## �� 部署

### 生产环境部署
1. 配置生产环境变量
2. 安装生产依赖：`pip install -r requirements/prod.txt`
3. 配置数据库 (PostgreSQL)
4. 配置Redis缓存
5. 收集静态文件：`python manage.py collectstatic`
6. 使用Gunicorn启动：`gunicorn wsgi:application`

### Docker部署 (推荐)
```bash
# 构建镜像
docker build -t modeshift .

# 运行容器
docker run -p 8000:8000 modeshift
```

## 📊 监控和日志

- 应用日志：`logs/django.log`
- 用户活动监控
- API使用统计
- 性能监控

## 🔒 安全特性

- CSRF保护
- XSS防护
- SQL注入防护
- 文件上传安全
- API访问限制
- 用户权限控制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

- 📧 邮箱：support@modeshift.com
- 📖 文档：[项目文档](docs/)
- 🐛 问题反馈：[Issues](../../issues)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**ModeShift** - 让工具使用更简单，让生活更高效！ 🎉

