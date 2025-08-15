# 聊天室问题诊断和解决方案

## 🔍 问题分析

聊天室功能无法使用的主要原因：

### 1. **WebSocket服务器问题**
- 聊天室需要ASGI服务器（Daphne）支持WebSocket
- 普通的Django开发服务器不支持WebSocket

### 2. **认证问题**
- 用户需要登录才能访问聊天室
- WebSocket连接需要用户认证

### 3. **路由配置问题**
- WebSocket路由可能配置不正确

## 🛠️ 解决方案

### 步骤1: 启动正确的服务器

停止当前的Django开发服务器，启动支持WebSocket的ASGI服务器：

```bash
# 停止当前服务器
pkill -f "python manage.py runserver"

# 启动ASGI服务器
python run_asgi_server.py
```

### 步骤2: 验证WebSocket连接

访问聊天室调试页面来测试WebSocket连接：

1. 登录系统
2. 访问: `http://localhost:8000/tools/chat/debug/test-room-123/`
3. 点击"连接WebSocket"按钮
4. 查看连接状态和调试信息

### 步骤3: 检查聊天室功能

#### 3.1 数字匹配功能
- 访问: `http://localhost:8000/tools/number-match/`
- 输入4位数字进行匹配

#### 3.2 直接聊天功能
- 访问: `http://localhost:8000/tools/chat/`
- 选择"直接聊天"或输入聊天室ID

#### 3.3 心动链接功能
- 访问: `http://localhost:8000/tools/heart_link/`
- 创建心动链接请求

## 🔧 技术细节

### WebSocket配置
```python
# asgi.py
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
```

### 聊天室模型
```python
class ChatRoom(models.Model):
    room_id = models.CharField(max_length=50, unique=True)
    user1 = models.ForeignKey(User, related_name='chat_rooms_as_user1')
    user2 = models.ForeignKey(User, related_name='chat_rooms_as_user2')
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES)
```

### WebSocket消费者
```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 检查用户认证和房间权限
        # 建立WebSocket连接
```

## 🚀 快速测试

### 1. 创建测试聊天室
```python
python manage.py shell -c "
from apps.tools.models import ChatRoom
from django.contrib.auth.models import User
user = User.objects.first()
room = ChatRoom.objects.create(room_id='test-room-123', user1=user, status='active')
print('Created room:', room.room_id)
"
```

### 2. 测试WebSocket连接
```javascript
// 在浏览器控制台中测试
const ws = new WebSocket('ws://localhost:8000/ws/chat/test-room-123/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', event.data);
```

## 📋 检查清单

- [ ] ASGI服务器正在运行
- [ ] 用户已登录
- [ ] 聊天室已创建
- [ ] WebSocket连接成功
- [ ] 消息可以发送和接收

## 🆘 常见问题

### Q: WebSocket连接失败
**A:** 确保使用ASGI服务器而不是Django开发服务器

### Q: 用户无法访问聊天室
**A:** 检查用户是否已登录，以及是否有权限访问该聊天室

### Q: 消息无法发送
**A:** 检查WebSocket连接状态和消息格式

### Q: 聊天室不存在
**A:** 创建聊天室或使用测试房间ID

## 📞 技术支持

如果问题仍然存在，请检查：

1. 服务器日志中的错误信息
2. 浏览器控制台的错误信息
3. WebSocket连接状态
4. 数据库中的聊天室记录
