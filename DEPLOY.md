# 🚀 QAToolBox 一键部署指南

## 快速部署（推荐）

### 一行命令部署

```bash
# 以root用户登录阿里云服务器后执行
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deployment/scripts/one_click_deploy.sh | bash
```

### 部署信息

- **服务器IP**: 47.103.143.152
- **域名**: shenyiqing.xin
- **安装目录**: /opt/QAToolbox
- **支持系统**: CentOS 7/8, Ubuntu 18.04+, Debian 10+

## 🔐 默认账户信息

| 服务 | 用户名 | 密码 | 用途 |
|------|--------|------|------|
| 系统用户 | qatoolbox | qatoolbox123 | SSH登录/sudo操作 |
| Django管理 | admin | admin123456 | 网站后台管理 |
| PostgreSQL | qatoolbox | 自动生成 | 数据库连接 |

## 📱 访问地址

- **网站首页**: http://47.103.143.152 或 http://shenyiqing.xin
- **管理后台**: http://shenyiqing.xin/admin/

## 🛠️ 服务管理

部署完成后使用以下命令管理服务：

```bash
cd /opt/QAToolbox

# 基本操作
./deployment/scripts/manage.sh start      # 启动服务
./deployment/scripts/manage.sh stop       # 停止服务
./deployment/scripts/manage.sh restart    # 重启服务
./deployment/scripts/manage.sh status     # 查看状态

# 维护操作
./deployment/scripts/manage.sh logs       # 查看日志
./deployment/scripts/manage.sh update     # 更新代码
./deployment/scripts/manage.sh backup     # 备份数据库
./deployment/scripts/manage.sh ssl        # 配置SSL证书
./deployment/scripts/manage.sh health     # 健康检查
```

## 📋 功能特性

部署包含以下完整功能：

### 🔧 工具集合
- ✅ PDF处理和转换
- ✅ 图像处理和编辑
- ✅ 音频文件转换
- ✅ Excel数据处理
- ✅ 思维导图生成
- ✅ 文档格式转换

### 🌐 社交媒体工具
- ✅ 小红书内容工具
- ✅ 抖音视频工具
- ✅ 微博数据分析
- ✅ B站视频工具
- ✅ 知乎内容工具

### 🤖 AI功能
- ✅ 智能问答系统
- ✅ 内容自动生成
- ✅ 文本分析处理
- ✅ 图像识别分析

### 💪 健身工具
- ✅ 训练计划制定
- ✅ 营养成分分析
- ✅ 健身数据跟踪
- ✅ 运动指导建议

### 📊 数据分析
- ✅ 图表生成工具
- ✅ 数据可视化
- ✅ 统计分析功能
- ✅ 报表生成系统

### 💰 金融工具
- ✅ 股票数据查询
- ✅ 财务数据分析
- ✅ 投资计算工具
- ✅ 市场趋势分析

## 🔧 高级配置

### API密钥配置

如需使用特定功能，请配置相应的API密钥：

```bash
# 编辑环境变量文件
vim /opt/QAToolbox/.env

# 添加您的API密钥
DEEPSEEK_API_KEY=your-api-key
GOOGLE_API_KEY=your-api-key
# ... 其他API配置

# 重启服务应用配置
./deployment/scripts/manage.sh restart
```

### SSL证书配置

```bash
cd /opt/QAToolbox
./deployment/scripts/manage.sh ssl
```

## 📚 详细文档

- [完整部署文档](deployment/docs/README.md)
- [故障排除指南](deployment/docs/README.md#故障排除)
- [API配置说明](deployment/docs/README.md#配置说明)

## 🆘 故障排除

### 常见问题

1. **服务启动失败**
```bash
./deployment/scripts/manage.sh logs
./deployment/scripts/manage.sh health
```

2. **网站无法访问**
```bash
# 检查防火墙
firewall-cmd --list-all  # CentOS
ufw status               # Ubuntu
```

3. **数据库连接问题**
```bash
./deployment/scripts/manage.sh logs db
```

### 获取帮助

```bash
./deployment/scripts/manage.sh help
```

## 📞 技术支持

- GitHub Issues: https://github.com/shinytsing/QAToolbox/issues
- 项目地址: https://github.com/shinytsing/QAToolbox

---

## 🎯 部署步骤总结

1. **连接服务器**: `ssh root@47.103.143.152`
2. **运行部署脚本**: `curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deployment/scripts/one_click_deploy.sh | bash`
3. **等待部署完成** (约10-15分钟)
4. **访问网站**: http://47.103.143.152
5. **登录管理后台**: http://shenyiqing.xin/admin/ (admin/admin123456)
6. **修改默认密码**
7. **配置SSL证书** (可选)
8. **享受使用！** 🎉

**就是这么简单！一条命令搞定所有部署！**
