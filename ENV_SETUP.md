# 环境变量配置说明

## 问题描述
如果遇到 `ValueError: DEEPSEEK_API_KEY 未在环境变量中设置` 错误，请按照以下步骤配置环境变量。

## 解决方案

### 方法1：使用 .env 文件（推荐）

1. 在项目根目录创建 `.env` 文件：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件，填入您的实际配置：
```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-your-actual-api-key-here

# Django 配置
DJANGO_SECRET_KEY=django-insecure-1^6^nfbpnl$vpi=o05c8n+%7#b@ldjegoj6u0-3*!t3a3m#*54
DJANGO_DEBUG=True

# API 速率限制配置
API_RATE_LIMIT=10/minute
```

3. 获取 DeepSeek API 密钥：
   - 访问 https://platform.deepseek.com/
   - 注册并登录您的账户
   - 在控制台中创建新的 API 密钥
   - 将密钥复制到 `.env` 文件中

### 方法2：设置系统环境变量

#### macOS/Linux:
```bash
export DEEPSEEK_API_KEY="sk-your-actual-api-key-here"
export API_RATE_LIMIT="10/minute"
```

#### Windows:
```cmd
set DEEPSEEK_API_KEY=sk-your-actual-api-key-here
set API_RATE_LIMIT=10/minute
```

### 方法3：在代码中直接设置（仅用于开发）

在 `settings.py` 文件中添加：
```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-actual-api-key-here'
```

## 验证配置

配置完成后，重启 Django 服务器：
```bash
python manage.py runserver
```

如果配置正确，错误应该消失。

## 注意事项

1. **安全性**：不要将包含真实 API 密钥的 `.env` 文件提交到版本控制系统
2. **备份**：确保 `.env` 文件已添加到 `.gitignore` 中
3. **权限**：确保 `.env` 文件只有您自己可以读取

## 故障排除

如果仍然遇到问题：

1. 检查 `.env` 文件是否在正确位置（项目根目录）
2. 确认 API 密钥格式正确（通常以 `sk-` 开头）
3. 验证 `python-dotenv` 包已安装：`pip install python-dotenv`
4. 重启 Django 服务器 