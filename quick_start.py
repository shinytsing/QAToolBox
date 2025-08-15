#!/usr/bin/env python
"""
QAToolBox 快速启动脚本
一键启动API服务和WebSocket聊天服务器
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

def main():
    """主函数"""
    print("🚀 QAToolBox 快速启动")
    print("=" * 40)
    
    # 检查是否存在统一启动脚本
    if not Path('start_unified_server.py').exists():
        print("❌ 未找到统一启动脚本，请先运行: python start_unified_server.py")
        return
    
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    try:
        print("📍 启动地址:")
        print("   🌐 主应用: http://localhost:8000")
        print("   🔌 WebSocket: ws://localhost:8000/ws/")
        print("   📱 API服务: http://localhost:8001")
        print("   💬 聊天功能: http://localhost:8000/tools/chat/")
        print("   ❤️  心动链接: http://localhost:8000/tools/heart_link/")
        print("")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("-" * 40)
        
        # 启动统一服务器
        subprocess.run([sys.executable, 'start_unified_server.py'])
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()
