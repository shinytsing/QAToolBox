# 🚀 QAToolBox 一行命令部署

## 📱 超简单部署 - 复制粘贴即可

### 在阿里云Ubuntu服务器上运行以下命令：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh)
```

就这么简单！🎉

## 🎯 部署完成后

- **访问地址**: `http://你的服务器IP`
- **管理后台**: `http://你的服务器IP/admin/`
- **默认账号**: `admin`
- **默认密码**: `admin123456`

## 🔧 备用部署方式

如果上面的命令无法访问，可以尝试：

```bash
# 方式1: 使用install.sh
bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/install.sh)

# 方式2: 手动克隆
git clone https://github.com/shinytsing/QAToolbox.git
cd QAToolbox
chmod +x deploy_china.sh
./deploy_china.sh
```

## ✨ 特点

- ✅ 适配中国网络环境
- ✅ 使用阿里云镜像源
- ✅ 自动安装所有依赖
- ✅ 一键完成部署
- ✅ 包含完整功能

## 📞 需要帮助？

查看详细文档: [DEPLOY_CHINA_README.md](DEPLOY_CHINA_README.md)

---
**真的就这么简单！** 🎊
