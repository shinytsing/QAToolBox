# QAToolBox Flutter App

基于 Flutter 的跨平台移动应用，提供健身管理、生活助手、极客工具和社交娱乐等功能。

## 技术栈

- **框架**: Flutter 3.10+
- **语言**: Dart 3.0+
- **状态管理**: Riverpod
- **路由**: GoRouter
- **网络请求**: Dio + Retrofit
- **本地存储**: Hive + SharedPreferences
- **UI组件**: Material Design 3
- **响应式设计**: flutter_screenutil
- **图表**: fl_chart
- **图片处理**: cached_network_image
- **权限管理**: permission_handler
- **推送通知**: firebase_messaging
- **二维码**: qr_flutter
- **文件处理**: file_picker
- **音频播放**: audioplayers
- **视频播放**: video_player
- **地图**: amap_flutter_map

## 功能特性

### 核心功能
- 🏠 **首页**: 个性化仪表盘，快速访问功能
- 💪 **健身管理**: 训练记录，数据统计，目标追踪
- 🌟 **生活助手**: 日记记录，食物推荐，冥想放松
- 🛠️ **极客工具**: PDF转换，代码格式化，数据分析
- 💬 **社交娱乐**: 聊天交友，心链连接，塔罗占卜
- 👤 **个人中心**: 资料管理，成就系统，数据统计

### 技术特性
- 🎨 **现代化UI**: Material Design 3，支持暗色主题
- 🔐 **统一登录**: 多端登录，设备管理，数据同步
- 📊 **数据可视化**: 丰富的图表展示，实时数据更新
- 🚀 **性能优化**: 代码分割，懒加载，缓存策略
- 📱 **跨平台**: 支持iOS和Android
- 🔧 **开发友好**: 代码生成，热重载，代码规范

## 项目结构

```
lib/
├── core/                    # 核心功能
│   ├── config/             # 配置文件
│   ├── models/             # 数据模型
│   ├── providers/          # 状态管理
│   ├── router/             # 路由配置
│   ├── services/           # 服务层
│   └── theme/              # 主题配置
├── features/               # 功能模块
│   ├── auth/               # 认证模块
│   ├── fitness/            # 健身模块
│   ├── geek/               # 极客工具模块
│   ├── home/               # 首页模块
│   ├── life/               # 生活助手模块
│   ├── profile/            # 个人中心模块
│   ├── social/             # 社交娱乐模块
│   └── splash/             # 启动页模块
└── main.dart               # 应用入口
```

## 开发指南

### 环境要求
- Flutter SDK >= 3.10.0
- Dart SDK >= 3.0.0
- Android SDK >= 21
- iOS >= 11.0

### 安装依赖
```bash
flutter pub get
```

### 代码生成
```bash
flutter packages pub run build_runner build
```

### 开发模式
```bash
flutter run
```

### 构建发布版本
```bash
# Android
flutter build apk --release

# iOS
flutter build ios --release
```

### 代码检查
```bash
flutter analyze
```

### 代码格式化
```bash
flutter format .
```

## 配置说明

### 环境配置
- 开发环境: `lib/core/config/app_config.dart`
- 生产环境: 根据实际部署环境配置

### API配置
- 基础URL: `https://your-api-domain.com/api/v1`
- 认证方式: JWT Token
- 响应格式: 统一JSON格式

### 主题配置
- 浅色主题: `lib/core/theme/app_theme.dart`
- 深色主题: 自动适配系统主题
- 自定义主题: 支持主题切换

## 部署说明

### Android部署
1. 配置签名文件
2. 执行构建命令
3. 上传到Google Play Store

### iOS部署
1. 配置开发者证书
2. 执行构建命令
3. 上传到App Store

## 开发规范

### 代码规范
- 使用 `very_good_analysis` 进行代码检查
- 遵循 Dart 官方代码规范
- 使用 `flutter format` 格式化代码

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 浏览器支持

- Android 5.0+
- iOS 11.0+

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
