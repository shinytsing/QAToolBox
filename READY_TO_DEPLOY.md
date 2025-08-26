# 🎯 QAToolBox 阿里云部署 - 立即可用版本

## 📍 服务器信息
- **IP地址**: 47.103.143.152
- **域名**: https://shenyiqing.xin/
- **GitHub仓库**: https://github.com/shinytsing/QAToolbox.git

## 🚀 立即部署命令

### 连接到阿里云服务器
```bash
ssh root@47.103.143.152
```

### 执行一键部署（三选一）

#### 🎯 方案1: 阿里云专用部署（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash
```

#### 🎯 方案2: 完整功能部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_with_all_deps.sh | sudo bash
```

#### 🎯 方案3: 快速部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_quick_start.sh | sudo bash
```

## 🧪 验证部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/test_deployment.sh | sudo bash
```

## ✅ 部署成功后访问
- 🌐 **主站**: http://shenyiqing.xin/
- 👑 **管理后台**: http://shenyiqing.xin/admin/
- 🔑 **默认账号**: admin / admin123456

## 📋 解决的依赖问题
- ✅ torch (深度学习)
- ✅ torchvision (计算机视觉) 
- ✅ opencv-python (图像处理)
- ✅ django-environ (环境变量)
- ✅ scikit-learn (机器学习)
- ✅ PostgreSQL (数据库)
- ✅ Redis (缓存)
- ✅ Nginx (Web服务器)

## 🔧 部署时间
- 预计时间: 10-20分钟
- 下载大小: ~2GB
- 内存需求: 2GB+

---

**注意**: 这些脚本已经包含了所有必要的依赖和配置，一次执行即可完成部署！

## 📞 如果需要其他信息

基于你的GitHub仓库 `https://github.com/shinytsing/QAToolbox.git`，我已经更新了所有部署脚本。

**还需要的信息（可选）:**

1. **SSL证书配置** - 如果要启用HTTPS，需要SSL证书文件
2. **域名DNS配置** - 确保 shenyiqing.xin 解析到 47.103.143.152
3. **邮件服务配置** - 如果需要发送邮件功能
4. **第三方API密钥** - 如果使用AI服务等

但这些都是可选的，基础部署不需要这些信息。现在你可以直接在服务器上执行上述命令进行部署！
