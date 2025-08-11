#!/usr/bin/env python3
"""
WebSocket连接测试脚本
"""

import asyncio
import websockets
import json
import uuid

async def test_websocket_connection():
    """测试WebSocket连接"""
    room_id = f"test-room-{uuid.uuid4()}"
    uri = f"ws://localhost:8000/ws/chat/{room_id}/"
    
    print(f"🔌 连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 发送测试消息
            test_message = {
                "type": "message",
                "content": "Hello from test client!",
                "message_type": "text"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 发送测试消息")
            
            # 接收响应
            response = await websocket.recv()
            print(f"📥 收到响应: {response}")
            
            # 等待一段时间
            await asyncio.sleep(2)
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接已关闭: {e}")
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")

if __name__ == "__main__":
    print("🚀 开始WebSocket连接测试...")
    asyncio.run(test_websocket_connection())
