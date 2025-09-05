# QAToolBox 用户界面

基于 Vue3 + TypeScript + Element Plus 的现代化用户界面。

## 技术栈

- **框架**: Vue 3.4
- **语言**: TypeScript
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite
- **图表**: ECharts
- **HTTP客户端**: Axios
- **代码规范**: ESLint + Prettier

## 功能特性

### 核心功能
- 🏠 **首页**: 个性化仪表盘，快速访问功能
- 💪 **健身管理**: 训练记录，数据统计，目标追踪
- 🌟 **生活助手**: 日记记录，食物推荐，冥想放松
- 🛠️ **极客工具**: PDF转换，代码格式化，数据分析
- 💬 **社交娱乐**: 聊天交友，心链连接，塔罗占卜
- 👤 **个人中心**: 资料管理，成就系统，数据统计

### 技术特性
- 🎨 **现代化UI**: 响应式设计，支持暗色主题
- 🔐 **统一登录**: 多端登录，设备管理，数据同步
- 📊 **数据可视化**: 丰富的图表展示，实时数据更新
- 🚀 **性能优化**: 代码分割，懒加载，缓存策略
- 📱 **移动端适配**: 响应式布局，触摸友好
- 🔧 **开发友好**: TypeScript支持，热重载，代码规范

## 项目结构

```
src/
├── api/                 # API接口
├── assets/              # 静态资源
│   ├── css/            # 样式文件
│   ├── images/         # 图片资源
│   └── icons/          # 图标资源
├── components/          # 组件库
├── layouts/            # 布局组件
├── router/             # 路由配置
├── stores/             # 状态管理
├── types/              # 类型定义
├── utils/              # 工具函数
└── views/              # 页面组件
```

## 开发指南

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
```

### 代码格式化
```bash
npm run format
```

## 部署说明

### 构建部署
1. 执行构建命令生成生产版本
2. 将 `dist` 目录部署到 Web 服务器
3. 配置 Nginx 反向代理到后端 API

### 环境配置
- 开发环境: `http://localhost:3001`
- 生产环境: 根据实际部署环境配置

## API 集成

### 后端 API
- 基础URL: `/api/v1`
- 认证方式: JWT Token
- 响应格式: 统一 JSON 格式

### 主要接口
- 用户认证: `/auth/*`
- 健身管理: `/fitness/*`
- 生活工具: `/life/*`
- 极客工具: `/tools/*`
- 社交娱乐: `/social/*`
- 分享管理: `/share/*`

## 浏览器支持

- Chrome >= 88
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
