# 心动链接测试和修复指南

## 问题诊断

1. **服务器状态**: ✅ Daphne ASGI服务器已启动
2. **WebSocket路由**: ✅ 路由配置正确
3. **Channels配置**: ✅ 使用内存后端
4. **聊天室数据**: ✅ 聊天室存在且状态为active

## 测试步骤

### 1. 基础WebSocket连接测试

```bash
# 在浏览器中打开测试页面
open http://localhost:8000/test_websocket.html
```

### 2. 用户登录测试

使用创建的测试用户：
- 用户A: test_user_a / testpass123
- 用户B: test_user_b / testpass123

登录页面: http://localhost:8000/users/login/

### 3. 心动链接聊天室测试

聊天室URL: http://localhost:8000/tools/heart_link/chat/0c38a502-25ad-47e7-9a37-15660a57d135/

## 功能测试清单

### A. 连接同步测试
- [ ] 用户A登录并进入聊天室
- [ ] 用户B登录并进入聊天室  
- [ ] 两个用户同时在线显示
- [ ] 连接状态正确显示

### B. 消息发送测试
- [ ] 文本消息发送和接收
- [ ] 表情符号发送
- [ ] 消息时间戳显示
- [ ] 已读状态更新

### C. 多媒体功能测试
- [ ] 图片上传和显示
- [ ] 语音录制和播放
- [ ] 文件上传和下载
- [ ] 视频通话邀请

### D. 实时功能测试
- [ ] 打字状态提示
- [ ] 心跳保持连接
- [ ] 断线重连机制
- [ ] 用户上线/下线通知

## 修复建议

1. **WebSocket认证问题**: 需要在WebSocket连接时传递认证信息
2. **CSRF Token**: 确保文件上传等功能有正确的CSRF token
3. **媒体文件路径**: 检查图片、音频文件的URL路径是否正确
4. **错误处理**: 完善WebSocket连接错误的处理逻辑

## 调试命令

```bash
# 查看daphne日志
tail -f logs/django.log

# 检查WebSocket连接
python manage.py shell -c "from apps.tools.models.chat_models import ChatRoom; print(ChatRoom.objects.filter(status='active').count())"

# 重启服务器
pkill -f daphne && daphne -b 0.0.0.0 -p 8000 -v 2 asgi:application
```
