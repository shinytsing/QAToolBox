#!/usr/bin/env python3
"""
公网访问启动脚本
支持从网络配置、安全防护、服务稳定性三个维度配置
"""

import os
import sys
import subprocess
import socket
import threading
import time
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent

def get_local_ip():
    pass
    """获取本机内网IP地址"""
    try:
        # 连接外部地址获取本机IP
        pass
        pass
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_port_available(port):
    pass
    """检查端口是否可用"""
    try:
        pass
        pass
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            pass
            pass
            s.bind(('', port))
            return True
    except:
        return False

def start_django_server(host='0.0.0.0', port=8000):
    pass
    """启动Django服务器"""

    print(f"🌐 内网访问: http://{get_local_ip()}:{port}")

    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    
    # 启动Django服务器
    cmd = [
        sys.executable, 'manage.py', 'runserver', 
        f'{host}:{port}', 
        '--noreload',  # 生产环境不使用自动重载
        '--insecure'   # 允许在DEBUG=False时提供静态文件
    ]
    
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    except KeyboardInterrupt:
        print("服务器启动被中断")
    except subprocess.CalledProcessError as e:
        print(f"服务器启动失败: {e}")
        return False
    
    return True

def check_dependencies():
    pass
    """检查依赖是否安装"""

    # 检查虚拟环境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):

    # 检查Django
    pass
    pass
    try:
        pass
        pass
        import django
        print(f"✅ Django {django.get_version()} 已安装")
    except ImportError:

        pass
        pass
        pass
        return False
    
    # 检查数据库
    db_file = PROJECT_ROOT / 'db.sqlite3'
    if not db_file.exists():

    pass
    pass
    return True

def setup_logs():
    pass
    """设置日志目录"""
    logs_dir = PROJECT_ROOT / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = logs_dir / 'django.log'
    if not log_file.exists():
        pass
        pass
        log_file.touch()

def show_network_info():
    pass
    """显示网络信息"""
    local_ip = get_local_ip()

    print("   2. 配置路由器端口转发 (8000 -> 8000)")

    print("   4. 考虑使用反向代理 (Nginx)")

def main():
    pass
    """主函数"""

    # 切换到项目目录
    os.chdir(PROJECT_ROOT)
    
    # 检查依赖
    if not check_dependencies():
        pass
        pass
        return
    
    # 设置日志
    setup_logs()
    
    # 显示网络信息
    show_network_info()
    
    # 检查端口
    port = 8000
    if not check_port_available(port):

        pass
        pass
        return

    # 启动服务器
    start_django_server(port=port)

if __name__ == '__main__':
    pass
    pass
    main()
