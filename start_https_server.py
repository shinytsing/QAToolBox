#!/usr/bin/env python
"""
QAToolBox HTTPS服务器启动脚本
使用自签名SSL证书启动HTTPS服务
"""

import os
import sys
import ssl
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

def start_https_server():
    """启动HTTPS Django服务器"""
    
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    # SSL证书路径
    cert_file = PROJECT_ROOT / 'ssl' / 'cert.pem'
    key_file = PROJECT_ROOT / 'ssl' / 'key.pem'
    
    # 检查SSL证书是否存在
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL证书文件不存在，请先运行以下命令生成证书：")
        print("mkdir -p ssl && cd ssl")
        print("openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj \"/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/OU=Dev/CN=192.168.0.118\"")
        return False
    
    print("🔐 启动HTTPS服务器...")
    print(f"📍 HTTPS地址: https://192.168.0.118:8443")
    print(f"📍 本地访问: https://localhost:8443")
    print("⚠️  浏览器会提示证书不安全，请点击'继续访问'")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        # 使用Django的runserver_plus启动HTTPS服务器
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--cert-file', str(cert_file),
            '--key-file', str(key_file),
            '0.0.0.0:8443'
        ]
        
        # 如果没有runserver_plus，使用gunicorn
        try:
            subprocess.run([sys.executable, '-c', 'import django_extensions'], check=True, capture_output=True)
            subprocess.run(cmd)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📝 使用Gunicorn启动HTTPS服务器...")
            
            # 使用gunicorn启动HTTPS
            gunicorn_cmd = [
                'gunicorn',
                '--bind', '0.0.0.0:8443',
                '--workers', '4',
                '--timeout', '300',
                '--certfile', str(cert_file),
                '--keyfile', str(key_file),
                '--access-logfile', '-',
                '--error-logfile', '-',
                'config.wsgi:application'
            ]
            subprocess.run(gunicorn_cmd)
            
    except KeyboardInterrupt:
        print("\n🛑 HTTPS服务器已停止")
    except Exception as e:
        print(f"❌ 启动HTTPS服务器失败: {e}")
        return False
    
    return True

if __name__ == '__main__':
    start_https_server()
