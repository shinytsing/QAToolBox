# QAToolBox 🛠️

一个功能丰富的测试工程师工具箱，集成了多种实用工具，支持多主题切换和现代化UI设计。

## ✨ 主要功能

- 🎨 **多主题系统**：极客、朋克、狂暴、Emo四种模式
- 🛠️ **工具集**：创意文案生成、PDF转换、姻缘分析、测试用例生成、网页爬虫
- 👥 **用户系统**：注册登录、个人资料、会员等级
- 🔧 **管理后台**：用户管理、公告系统、数据监控

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Django 4.2.18

### 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolBox

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements/base.txt

# 4. 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 5. 数据库迁移
python manage.py migrate

# 6. 创建超级用户
python manage.py createsuperuser

# 7. 启动服务器
python manage.py runserver
```

访问 http://localhost:8000 开始使用！

## 📁 项目结构

```
QAToolBox/
├── apps/              # Django应用
├── templates/         # 模板文件
├── src/static/        # 静态资源
├── media/            # 媒体文件
├── requirements/     # 依赖管理
└── config/          # 配置文件
```

## 📚 详细文档

- [项目总结](PROJECT_SUMMARY.md) - 完整功能说明
- [工具页面功能](TOOL_PAGES_FUNCTIONALITY_SUMMARY.md) - 工具使用指南

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 开发者

**沈奕清** - AI使用者

- 📧 邮箱：通过关于页面获取
- 💼 简历：[/media/高杰-测试工程师.pdf](/media/高杰-测试工程师.pdf)
- 🎵 网易云：[关注我的音乐](https://music.163.com/#/user/home?id=555356040)
- 📖 GitHub：[查看源码](https://github.com/shinytsing/QAToolbox)

