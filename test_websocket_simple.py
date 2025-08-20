#!/usr/bin/env python3
"""
简单的WebSocket连接测试
"""

import asyncio
import websockets
import json

async def test_simple_websocket():
    """简单的WebSocket连接测试"""
    room_id = "test-room-123"
    ws_url = f"ws://localhost:8000/ws/chat/{room_id}/"
    
    print(f"🔗 测试WebSocket连接: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 等待连接消息
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 收到消息: {data}")
            except asyncio.TimeoutError:
                print("⏰ 等待消息超时")
            
            # 发送测试消息
            test_message = {
                "type": "chat_message",
                "content": "测试消息",
                "message_type": "text"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 发送测试消息")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📨 收到响应: {data}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时")
            
    except Exception as e:
        print(f"❌ WebSocket连接失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple_websocket())
