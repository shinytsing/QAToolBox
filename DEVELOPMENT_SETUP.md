# QAToolBox 开发环境安装指南

## 🎯 项目概述

QAToolBox 是一个多平台项目，包含：
- **后端**: Django + DRF + PostgreSQL
- **前端**: Vue3 管理后台 + Vue3 用户界面
- **小程序**: 微信小程序
- **移动端**: Flutter 应用

## ✅ 已完成的安装

### 1. 后端环境
- ✅ Python 3.13
- ✅ Django 4.2.7
- ✅ PostgreSQL
- ✅ JWT 认证系统

### 2. 前端环境
- ✅ Node.js 18+
- ✅ Vue3 管理后台 (运行在 http://localhost:3000)
- ✅ Vue3 用户界面 (运行在 http://localhost:5173)
- ✅ Element Plus UI 组件库

### 3. 开发工具
- ✅ 微信开发者工具 (已安装)

## 🔧 需要手动安装的环境

### 1. Flutter 环境 (移动端开发)

由于网络问题，需要手动安装 Flutter：

#### 方法一：使用官方安装包
```bash
# 1. 下载 Flutter SDK
cd ~/development
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_arm64_3.24.5-stable.zip

# 2. 解压
unzip flutter_macos_arm64_3.24.5-stable.zip

# 3. 添加到 PATH
echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zshrc
source ~/.zshrc

# 4. 验证安装
flutter doctor
```

#### 方法二：使用 Git 克隆
```bash
# 1. 克隆 Flutter 仓库
cd ~/development
git clone https://github.com/flutter/flutter.git -b stable

# 2. 添加到 PATH
echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zshrc
source ~/.zshrc

# 3. 验证安装
flutter doctor
```

### 2. Android Studio (Android 开发)

```bash
# 安装 Android Studio
brew install --cask android-studio
```

### 3. Xcode (iOS 开发)

```bash
# 安装 Xcode (需要从 App Store 安装)
# 或者安装 Xcode Command Line Tools
xcode-select --install
```

## 🚀 启动项目

### 1. 启动后端服务
```bash
cd /Users/gaojie/Desktop/PycharmProjects/QAToolBox
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 2. 启动前端服务
```bash
# 管理后台
cd frontend/admin-dashboard
npm run dev -- --port 3000

# 用户界面
cd frontend/user-interface
npm run dev -- --port 5173
```

### 3. 启动微信小程序
1. 打开微信开发者工具
2. 导入项目：`/Users/gaojie/Desktop/PycharmProjects/QAToolBox/miniprogram/wechat`
3. 配置 AppID（测试号即可）

### 4. 启动 Flutter 应用
```bash
cd mobile/flutter
flutter pub get
flutter run
```

## 📱 访问地址

| 服务 | 地址 | 状态 |
|------|------|------|
| Django 后端 | http://localhost:8000 | ✅ 运行中 |
| Vue3 管理后台 | http://localhost:3000 | ✅ 运行中 |
| Vue3 用户界面 | http://localhost:5173 | ✅ 运行中 |
| 微信小程序 | 微信开发者工具 | 🟡 需要配置 |
| Flutter 应用 | 模拟器/真机 | 🟡 需要 Flutter 环境 |

## 🔑 默认登录信息

- **用户名**: testuser
- **密码**: testpass123
- **设备类型**: web

## 🛠️ 开发工具推荐

### 代码编辑器
- **VS Code** (推荐)
  - Vue 3 插件
  - Flutter 插件
  - Python 插件
  - 微信小程序插件

### 数据库管理
- **pgAdmin** (PostgreSQL 管理)
- **DBeaver** (通用数据库工具)

### API 测试
- **Postman** (API 测试)
- **Insomnia** (轻量级 API 客户端)

## 📚 项目结构

```
QAToolBox/
├── api/                     # 后端 API
├── frontend/               # 前端项目
│   ├── admin-dashboard/    # Vue3 管理后台
│   └── user-interface/     # Vue3 用户界面
├── miniprogram/            # 小程序
│   └── wechat/             # 微信小程序
├── mobile/                 # 移动端
│   └── flutter/            # Flutter 应用
├── docs/                   # 文档
└── scripts/                # 脚本
```

## 🐛 常见问题

### 1. 用户界面 logo 错误
```bash
# 清除 Vite 缓存
rm -rf node_modules/.vite
npm run dev
```

### 2. 端口被占用
```bash
# 查找占用端口的进程
lsof -ti:8000
# 杀死进程
kill -9 <PID>
```

### 3. 数据库连接失败
```bash
# 检查 PostgreSQL 状态
brew services list | grep postgresql
# 启动 PostgreSQL
brew services start postgresql
```

## 📞 技术支持

- **项目文档**: `/docs/` 目录
- **API 文档**: http://localhost:8000/api/v1/
- **日志文件**: `/logs/django.log`

---

**最后更新**: 2025-09-06  
**项目状态**: 🟢 核心服务正常运行  
**下一步**: 完成 Flutter 环境配置，开始功能开发
