# QAToolBox CentOS阿里云部署指南

## 🚀 一键部署

在你的CentOS阿里云服务器上运行以下命令即可完成部署：

```bash
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/aliyun_deploy_centos.sh | bash
```

## 🖥️ 支持的CentOS版本

- ✅ **CentOS 7** (使用yum)
- ✅ **CentOS 8** (使用dnf)
- ✅ **Rocky Linux 8/9** (使用dnf)
- ✅ **AlmaLinux 8/9** (使用dnf)
- ✅ **RHEL 7/8/9** (使用yum/dnf)

## 📋 CentOS特有配置

### 包管理器自动检测
脚本会自动检测并使用合适的包管理器：
- **CentOS 7**: yum
- **CentOS 8+**: dnf
- **Rocky/Alma Linux**: dnf

### 防火墙配置
脚本会自动配置防火墙：

#### Firewalld (推荐)
```bash
# 查看防火墙状态
sudo firewall-cmd --state

# 查看开放的端口
sudo firewall-cmd --list-all

# 手动开放端口
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

#### Iptables (备选)
```bash
# 查看iptables规则
sudo iptables -L

# 保存规则
sudo service iptables save
```

### SELinux配置
如果启用了SELinux，脚本会自动配置：

```bash
# 查看SELinux状态
getenforce

# 查看SELinux策略
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_enable_homedirs 1

# 如果需要禁用SELinux (不推荐)
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

## 🔧 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 40GB
- **系统**: CentOS 7+

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 80GB SSD
- **系统**: CentOS 8+ 或 Rocky Linux 9

## 📦 自动安装的软件包

### 基础软件
- curl, wget, git, unzip
- epel-release
- Development Tools
- openssl-devel, libffi-devel, python3-devel

### 服务软件
- Docker CE + Docker Compose
- Nginx
- Certbot (SSL证书)

### 防火墙工具
- firewalld (优先)
- iptables-services (备选)

### SELinux工具
- policycoreutils-python-utils

## 🚀 部署流程

1. **系统检查**: 检测CentOS版本和包管理器
2. **系统更新**: 更新所有系统包
3. **基础软件**: 安装必要的开发工具和依赖
4. **Docker安装**: 安装Docker CE和Docker Compose
5. **Web服务**: 安装Nginx和SSL工具
6. **防火墙配置**: 配置firewalld或iptables
7. **SELinux配置**: 如果启用则自动配置
8. **项目部署**: 克隆代码并配置环境
9. **服务启动**: 构建镜像并启动所有服务
10. **系统服务**: 注册为系统服务，开机自启

## 🛠️ 服务管理

```bash
cd ~/QAToolbox

# 基础操作
./manage_service.sh start     # 启动服务
./manage_service.sh stop      # 停止服务
./manage_service.sh restart   # 重启服务
./manage_service.sh status    # 查看状态
./manage_service.sh logs      # 查看日志

# 高级操作
./manage_service.sh update    # 更新代码
./manage_service.sh backup    # 备份数据
./manage_service.sh ssl       # 配置SSL
```

## 🔍 CentOS特有故障排除

### 1. 防火墙问题
```bash
# 检查防火墙状态
sudo systemctl status firewalld

# 重启防火墙
sudo systemctl restart firewalld

# 查看开放端口
sudo firewall-cmd --list-ports

# 临时关闭防火墙测试
sudo systemctl stop firewalld
```

### 2. SELinux问题
```bash
# 查看SELinux日志
sudo ausearch -m avc -ts recent

# 临时设置为宽松模式
sudo setenforce 0

# 生成SELinux策略
sudo audit2allow -a
```

### 3. Docker权限问题
```bash
# 重新加载用户组
newgrp docker

# 或者重新登录SSH
exit
# 重新SSH连接
```

### 4. 包管理器问题
```bash
# 清理yum缓存
sudo yum clean all

# 清理dnf缓存
sudo dnf clean all

# 更新包管理器
sudo yum update -y
# 或
sudo dnf update -y
```

### 5. 网络连接问题
```bash
# 检查DNS
nslookup google.com

# 检查网络连接
ping -c 4 8.8.8.8

# 检查代理设置
echo $http_proxy
echo $https_proxy
```

## 🔒 安全配置

### 防火墙最佳实践
```bash
# 只开放必要端口
sudo firewall-cmd --permanent --remove-service=dhcpv6-client
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SELinux最佳实践
```bash
# 保持SELinux启用，只配置必要的布尔值
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_enable_homedirs 1

# 不要禁用SELinux，而是配置正确的上下文
sudo restorecon -Rv /home/$USER/QAToolbox/
```

### SSH安全配置
```bash
# 修改SSH端口 (可选)
sudo sed -i 's/#Port 22/Port 2222/g' /etc/ssh/sshd_config
sudo systemctl restart sshd
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --reload
```

## 📊 性能优化

### 系统调优
```bash
# 增加文件描述符限制
echo "* soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65535" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Docker优化
```bash
# 配置Docker日志轮转
sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

## 🔄 系统更新

### 定期维护
```bash
# 更新系统
sudo yum update -y  # CentOS 7
sudo dnf update -y  # CentOS 8+

# 清理旧内核
sudo package-cleanup --oldkernels --count=2  # CentOS 7
sudo dnf remove $(dnf repoquery --installonly --latest-limit=-2 -q)  # CentOS 8+

# 重启系统 (如果需要)
sudo reboot
```

### 自动更新 (可选)
```bash
# CentOS 7
sudo yum install -y yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron

# CentOS 8+
sudo dnf install -y dnf-automatic
sudo systemctl enable dnf-automatic.timer
sudo systemctl start dnf-automatic.timer
```

## 📞 技术支持

如遇到CentOS特有问题：

1. **查看系统日志**: `sudo journalctl -xe`
2. **查看服务状态**: `sudo systemctl status qatoolbox`
3. **查看防火墙**: `sudo firewall-cmd --list-all`
4. **查看SELinux**: `sudo ausearch -m avc -ts recent`

---

**CentOS部署完成！享受使用QAToolBox！** 🎉
