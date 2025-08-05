# Boss直聘自动求职机API功能说明

## 🎯 功能概述

自动求职机已升级，新增Boss直聘扫码登录和自动发送联系请求功能。用户可以通过扫码登录Boss直聘，系统会自动搜索匹配的职位并发送联系请求。

## 🔧 核心功能

### 1. 扫码登录
- **二维码生成**: 系统自动生成Boss直聘登录二维码
- **状态轮询**: 实时检查扫码登录状态
- **会话管理**: 自动管理登录会话和Cookie

### 2. 职位搜索
- **智能筛选**: 根据职位名称、地点、薪资等条件搜索
- **匹配算法**: 计算职位与用户需求的匹配度
- **批量处理**: 支持多页搜索结果处理

### 3. 自动联系
- **联系请求**: 自动向匹配的职位发送联系请求
- **状态跟踪**: 实时跟踪联系请求状态
- **频率控制**: 可配置发送间隔，避免过于频繁

## 📁 文件结构

```
apps/tools/
├── services/
│   ├── boss_zhipin_api.py          # Boss直聘API服务
│   └── job_search_service.py       # 求职服务（已更新）
├── views.py                        # 视图函数（已更新）
├── urls.py                         # URL配置（已更新）
└── templates/tools/
    └── job_search_machine.html     # 求职机页面（已更新）
```

## 🚀 使用方法

### 1. 安装依赖
```bash
pip install qrcode==7.4.2
```

### 2. 访问求职机
访问 `/tools/job-search-machine/` 页面

### 3. 扫码登录
1. 点击"扫码登录"按钮
2. 使用Boss直聘APP扫描二维码
3. 在APP中确认登录
4. 系统自动检测登录状态

### 4. 创建求职请求
1. 填写职位要求（职位名称、地点、薪资等）
2. 设置筛选条件（工作类型、经验要求等）
3. 配置自动投递参数（最大数量、间隔时间）
4. 提交请求开始自动求职

## 🔌 API接口

### 1. 生成二维码
```
GET /tools/api/boss/qr-code/
```

### 2. 检查登录状态
```
GET /tools/api/boss/check-login/
```

### 3. 获取登录状态
```
GET /tools/api/boss/login-status/
```

### 4. 退出登录
```
POST /tools/api/boss/logout/
```

### 5. 发送联系请求
```
POST /tools/api/boss/send-contact/
Content-Type: application/json

{
    "job_id": "职位ID"
}
```

## 🔧 技术实现

### 1. Boss直聘API服务 (`boss_zhipin_api.py`)

```python
class BossZhipinAPI:
    def generate_qr_code(self) -> Dict:
        """生成登录二维码"""
        
    def check_qr_login_status(self, qr_code_id: str) -> Dict:
        """检查二维码登录状态"""
        
    def search_jobs(self, **kwargs) -> Dict:
        """搜索职位"""
        
    def send_contact_request(self, job_id: str) -> Dict:
        """发送联系请求"""
```

### 2. 求职服务 (`job_search_service.py`)

```python
class JobSearchService:
    def generate_qr_code(self, user_id: int) -> Dict:
        """生成二维码（带缓存）"""
        
    def check_qr_login_status(self, user_id: int) -> Dict:
        """检查登录状态（带缓存）"""
        
    def start_auto_job_search(self, job_request: JobSearchRequest) -> Dict:
        """开始自动求职（已更新为发送联系请求）"""
```

### 3. 缓存机制

- **二维码缓存**: 5分钟过期，避免重复生成
- **登录状态缓存**: 1小时过期，保持登录状态
- **Redis存储**: 使用Django缓存框架

## 📊 联系请求参数

根据提供的curl命令，联系请求包含以下关键参数：

```bash
# 请求URL
https://www.zhipin.com/wapi/zpgeek/friend/add.json

# 关键参数
- jobId: 职位ID
- securityId: 安全ID（用于验证请求）
- lid: 会话ID
- token: 用户认证token
- zp_token: Boss直聘token
- traceId: 请求追踪ID
```

## 🛡️ 安全考虑

### 1. 反爬虫处理
- 模拟真实浏览器请求头
- 随机化请求间隔
- 使用真实的User-Agent

### 2. 会话管理
- 自动管理Cookie和Session
- 登录状态缓存和过期处理
- 安全的退出登录机制

### 3. 频率限制
- 可配置的请求间隔
- 最大投递数量限制
- 智能匹配度筛选

## 🧪 测试

运行测试脚本验证功能：

```bash
python test_boss_zhipin_api.py
```

测试内容包括：
- 二维码生成和登录状态检查
- 职位搜索功能
- 联系请求发送
- 登录状态管理

## 📝 注意事项

1. **合规使用**: 请遵守Boss直聘的使用条款和robots.txt
2. **频率控制**: 建议设置合理的请求间隔，避免被限制
3. **数据保护**: 用户登录信息仅用于求职功能，不会泄露
4. **功能限制**: 由于反爬虫机制，某些功能可能需要手动处理

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✅ 新增Boss直聘扫码登录功能
- ✅ 新增自动发送联系请求功能
- ✅ 优化职位搜索和匹配算法
- ✅ 添加登录状态管理和缓存
- ✅ 更新前端界面，支持扫码登录

### v1.0.0 (原版本)
- ✅ 基础求职请求创建
- ✅ 模拟职位搜索和投递
- ✅ 申请记录管理

## 🤝 贡献

欢迎提交Issue和Pull Request来改进功能！

## 📄 许可证

本项目遵循MIT许可证。 