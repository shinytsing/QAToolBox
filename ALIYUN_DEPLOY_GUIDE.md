# QAToolBox 阿里云部署指南

## 服务器信息
- **服务器IP**: 47.103.143.152
- **内网IP**: 172.24.33.31
- **用户名**: root
- **密码**: GJc9d5&b5z
- **域名**: shenyiqing.xin

## 部署步骤

### 1. 连接服务器
```bash
ssh root@47.103.143.152
# 输入密码: GJc9d5&b5z
```

### 2. 上传项目代码
在本地执行以下命令上传代码到服务器：
```bash
# 从本地Mac上传代码到服务器
scp -r /Users/gaojie/Desktop/PycharmProjects/QAToolBox/* root@47.103.143.152:/home/qatoolbox/QAToolBox/
```

### 3. 在服务器上运行部署脚本
```bash
# 在服务器上执行
cd /home/qatoolbox/QAToolBox
chmod +x deploy_gaojie_aliyun.sh
sudo ./deploy_gaojie_aliyun.sh
```

### 4. 配置域名解析
确保域名 `shenyiqing.xin` 和 `www.shenyiqing.xin` 都解析到 `47.103.143.152`

### 5. 访问应用
部署完成后，可以通过以下地址访问：
- **主站**: http://shenyiqing.xin/
- **IP访问**: http://47.103.143.152/
- **管理后台**: http://shenyiqing.xin/admin/

### 6. 管理员账户
- **用户名**: admin
- **密码**: admin123456
- **邮箱**: admin@shenyiqing.xin

## 管理命令

### 重启应用
```bash
sudo supervisorctl restart qatoolbox
```

### 查看日志
```bash
# 应用日志
sudo tail -f /var/log/qatoolbox/gunicorn.log

# 错误日志
sudo tail -f /var/log/qatoolbox/gunicorn_error.log

# Nginx日志
sudo tail -f /var/log/nginx/access.log
```

### 重启服务
```bash
# 重启Nginx
sudo systemctl restart nginx

# 重启PostgreSQL
sudo systemctl restart postgresql

# 重启Redis
sudo systemctl restart redis-server
```

### 检查服务状态
```bash
# 检查所有服务状态
sudo supervisorctl status
sudo systemctl status nginx postgresql redis-server
```

## 故障排除

### 如果部署失败
1. 检查日志文件：`/tmp/qatoolbox_deploy_*.log`
2. 确保所有依赖都已安装
3. 检查数据库连接
4. 验证文件权限

### 如果无法访问网站
1. 检查防火墙设置：`sudo ufw status`
2. 检查Nginx配置：`sudo nginx -t`
3. 检查端口是否开放：`sudo netstat -tlnp | grep :80`

### 如果数据库连接失败
1. 检查PostgreSQL状态：`sudo systemctl status postgresql`
2. 检查数据库用户权限
3. 验证环境变量配置

## 安全建议

1. **修改默认密码**：部署完成后立即修改管理员密码
2. **配置SSL**：建议使用Let's Encrypt配置HTTPS
3. **定期备份**：设置自动备份数据库和媒体文件
4. **监控日志**：定期检查应用和系统日志

## 性能优化

1. **启用Gzip压缩**：已在Nginx配置中启用
2. **静态文件缓存**：已配置静态文件缓存策略
3. **数据库优化**：可根据需要调整PostgreSQL配置
4. **监控资源使用**：使用htop等工具监控系统资源

## 联系支持

如果遇到问题，请检查：
1. 部署日志文件
2. 系统服务状态
3. 网络连接
4. 文件权限设置
