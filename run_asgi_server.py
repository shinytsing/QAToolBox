#!/usr/bin/env python
"""
ASGI服务器启动脚本
用于支持WebSocket连接
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if __name__ == '__main__':
    try:
        import django
        django.setup()
        
        from daphne.server import Server
        from asgi import application
        
        print("🚀 启动ASGI服务器 (支持WebSocket)...")
        print("📍 服务器地址: http://localhost:8000")
        print("🔌 WebSocket地址: ws://localhost:8000/ws/")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动Daphne服务器
        from daphne.server import Server
        from daphne.endpoints import build_endpoint_description_strings
        
        # 配置端点
        endpoints = build_endpoint_description_strings(host='0.0.0.0', port=8000)
        
        # 启动服务器
        server = Server(application, endpoints=endpoints)
        server.run()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements/dev.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
