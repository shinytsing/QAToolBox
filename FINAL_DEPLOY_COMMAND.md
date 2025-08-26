# 🎯 QAToolBox 最终部署命令

## 🚀 在阿里云服务器 47.103.143.152 上一键部署

### 第一步：连接服务器
```bash
ssh root@47.103.143.152
```

### 第二步：执行一键部署命令

#### 方案1：阿里云专用脚本（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash
```

#### 方案2：完整功能部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_complete_with_all_deps.sh | sudo bash
```

#### 方案3：快速部署（最小安装）
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_quick_start.sh | sudo bash
```

### 第三步：验证部署
```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/test_deployment.sh | sudo bash
```

## ✅ 部署成功标志

看到以下信息表示部署成功：

```
========================================
🎉 QAToolBox 阿里云部署完成！
========================================

🌐 访问地址:
  - http://shenyiqing.xin/
  - http://47.103.143.152/

👑 管理员登录:
  - 用户名: admin
  - 密码: admin123456
  - 后台: http://shenyiqing.xin/admin/

✅ 已安装的关键依赖:
  - ✅ Django (Web框架)
  - ✅ PyTorch (深度学习)
  - ✅ OpenCV (计算机视觉)
  - ✅ Django-Environ (环境变量)
  - ✅ PostgreSQL (数据库)
  - ✅ Redis (缓存)
  - ✅ Nginx (Web服务器)
```

## 🎯 立即可用的功能

部署完成后，以下功能立即可用：

1. **网站访问** - http://shenyiqing.xin/
2. **管理后台** - http://shenyiqing.xin/admin/
3. **AI图像识别** - 支持torch和opencv
4. **数据管理** - PostgreSQL数据库
5. **缓存系统** - Redis缓存
6. **文件上传** - 支持图片、文档等
7. **API接口** - RESTful API

## 🔧 常用管理命令

```bash
# 重启应用
sudo supervisorctl restart qatoolbox

# 查看状态
sudo supervisorctl status

# 查看日志
sudo tail -f /var/log/qatoolbox.log

# 重启所有服务
sudo systemctl restart nginx postgresql redis-server supervisor
```

## 📂 重要路径

- **项目目录**: `/home/qatoolbox/QAToolBox`
- **虚拟环境**: `/home/qatoolbox/QAToolBox/.venv`
- **配置文件**: `/home/qatoolbox/QAToolBox/.env`
- **日志文件**: `/var/log/qatoolbox.log`
- **静态文件**: `/var/www/qatoolbox/static/`

## 🆘 如果部署失败

1. **查看错误日志**：
```bash
tail -f /var/log/qatoolbox_error.log
```

2. **重新运行部署**：
```bash
# 部署脚本是幂等的，可以安全重复运行
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash
```

3. **手动修复权限**：
```bash
sudo chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
```

## 🎉 恭喜！

执行完上述命令后，你将拥有一个完整的、生产就绪的、包含AI功能的Web应用！

---

**注意**: 确保你的GitHub仓库中包含所有必要的部署文件，替换命令中的 `YOUR_USERNAME` 为你的实际GitHub用户名。
