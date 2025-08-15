#!/usr/bin/env python
"""
QAToolBox 统一服务器启动脚本
同时启动API服务和WebSocket聊天服务器
"""

import os
import sys
import subprocess
import threading
import time
import signal
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 全局变量存储进程
processes = []
stop_event = threading.Event()

def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭服务器"""
    print("\n🛑 收到停止信号，正在关闭服务器...")
    stop_event.set()
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    sys.exit(0)

def check_dependencies():
    """检查必要的依赖是否安装"""
    required_packages = ['django', 'channels', 'daphne']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements/dev.txt")
        return False
    
    return True

def start_asgi_server():
    """启动ASGI服务器（支持WebSocket）"""
    print("🚀 启动ASGI服务器 (支持WebSocket)...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
        
        # 启动ASGI服务器
        process = subprocess.Popen([
            sys.executable, 'run_asgi_server.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        processes.append(process)
        
        # 监控输出
        while process.poll() is None and not stop_event.is_set():
            output = process.stdout.readline()
            if output:
                print(f"[ASGI] {output.strip()}")
            time.sleep(0.1)
        
        if process.returncode and not stop_event.is_set():
            print(f"❌ ASGI服务器异常退出，返回码: {process.returncode}")
            
    except Exception as e:
        print(f"❌ 启动ASGI服务器失败: {e}")

def start_django_server():
    """启动Django开发服务器（API服务）"""
    print("🌐 启动Django开发服务器 (API服务)...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
        
        # 启动Django开发服务器
        process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8001'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        processes.append(process)
        
        # 监控输出
        while process.poll() is None and not stop_event.is_set():
            output = process.stdout.readline()
            if output:
                print(f"[Django] {output.strip()}")
            time.sleep(0.1)
        
        if process.returncode and not stop_event.is_set():
            print(f"❌ Django服务器异常退出，返回码: {process.returncode}")
            
    except Exception as e:
        print(f"❌ 启动Django服务器失败: {e}")

def start_redis_server():
    """启动Redis服务器（如果未运行）"""
    print("🔍 检查Redis服务器...")
    
    try:
        # 检查Redis是否已运行
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis服务器已运行")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  Redis服务器未运行，尝试启动...")
    try:
        # 尝试启动Redis
        process = subprocess.Popen(['redis-server'], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        time.sleep(2)  # 等待Redis启动
        
        # 检查是否启动成功
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis服务器启动成功")
            processes.append(process)
            return True
        else:
            print("❌ Redis服务器启动失败")
            return False
    except FileNotFoundError:
        print("❌ Redis未安装，请先安装Redis")
        return False

def run_migrations():
    """运行数据库迁移"""
    print("🗄️  运行数据库迁移...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], check=True, capture_output=True, text=True)
        print("✅ 数据库迁移完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def collect_static():
    """收集静态文件"""
    print("📁 收集静态文件...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], check=True, capture_output=True, text=True)
        print("✅ 静态文件收集完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 静态文件收集失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QAToolBox 统一服务器启动脚本')
    parser.add_argument('--port', type=int, default=8000, help='ASGI服务器端口 (默认: 8000)')
    parser.add_argument('--api-port', type=int, default=8001, help='API服务器端口 (默认: 8001)')
    parser.add_argument('--no-redis', action='store_true', help='跳过Redis检查')
    parser.add_argument('--no-migrate', action='store_true', help='跳过数据库迁移')
    parser.add_argument('--no-static', action='store_true', help='跳过静态文件收集')
    parser.add_argument('--asgi-only', action='store_true', help='仅启动ASGI服务器')
    parser.add_argument('--api-only', action='store_true', help='仅启动API服务器')
    
    args = parser.parse_args()
    
    print("🎯 QAToolBox 统一服务器启动脚本")
    print("=" * 60)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行数据库迁移
    if not args.no_migrate:
        if not run_migrations():
            sys.exit(1)
    
    # 收集静态文件
    if not args.no_static:
        if not collect_static():
            sys.exit(1)
    
    # 启动Redis（如果需要）
    if not args.no_redis:
        if not start_redis_server():
            print("⚠️  继续启动其他服务...")
    
    print("\n🚀 启动服务器...")
    print(f"📍 ASGI服务器: http://localhost:{args.port}")
    print(f"📍 API服务器: http://localhost:{args.api_port}")
    print(f"🔌 WebSocket: ws://localhost:{args.port}/ws/")
    print("⏹️  按 Ctrl+C 停止所有服务器")
    print("-" * 60)
    
    # 启动服务器线程
    threads = []
    
    if not args.api_only:
        # 启动ASGI服务器
        asgi_thread = threading.Thread(target=start_asgi_server, daemon=True)
        asgi_thread.start()
        threads.append(asgi_thread)
    
    if not args.asgi_only:
        # 启动Django API服务器
        django_thread = threading.Thread(target=start_django_server, daemon=True)
        django_thread.start()
        threads.append(django_thread)
    
    # 等待线程完成
    try:
        while not stop_event.is_set():
            time.sleep(1)
            # 检查是否有进程异常退出
            for process in processes:
                if process and process.poll() is not None:
                    print(f"⚠️  检测到进程异常退出，返回码: {process.returncode}")
                    stop_event.set()
                    break
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号...")
        stop_event.set()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=5)
    
    print("👋 所有服务器已停止")

if __name__ == '__main__':
    main()
