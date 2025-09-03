#!/usr/bin/env python3
"""
QAToolBox 服务状态检查脚本
检查Cloudflare域名和本地服务的状态
"""

import requests
import subprocess
import sys
import time
from datetime import datetime

def check_local_service():
    """检查本地服务状态"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_cloudflare_domain():
    """检查Cloudflare域名状态"""
    try:
        response = requests.get('https://shenyiqing.xin/', timeout=10)
        return response.status_code == 200
    except:
        return False

def check_gunicorn_processes():
    """检查Gunicorn进程状态"""
    try:
        result = subprocess.run(['pgrep', '-f', 'gunicorn'], 
                              capture_output=True, text=True)
        processes = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return len(processes) >= 5  # 1个主进程 + 4个工作进程
    except:
        return False

def main():
    print("🔍 QAToolBox 服务状态检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查本地服务
    local_status = check_local_service()
    print(f"📍 本地服务 (localhost:8000): {'✅ 正常' if local_status else '❌ 异常'}")
    
    # 检查Cloudflare域名
    domain_status = check_cloudflare_domain()
    print(f"🌐 Cloudflare域名 (https://shenyiqing.xin): {'✅ 正常' if domain_status else '❌ 异常'}")
    
    # 检查Gunicorn进程
    gunicorn_status = check_gunicorn_processes()
    print(f"🚀 Gunicorn进程: {'✅ 正常' if gunicorn_status else '❌ 异常'}")
    
    print()
    print("📊 服务状态总结:")
    if all([local_status, domain_status, gunicorn_status]):
        print("🎉 所有服务运行正常！")
        print("🌐 可通过 https://shenyiqing.xin 访问")
        print("📍 本地访问: http://localhost:8000")
        print("🏠 内网访问: http://192.168.0.118:8000")
    else:
        print("⚠️  部分服务异常，请检查配置")
        if not local_status:
            print("   - 本地服务无法访问")
        if not domain_status:
            print("   - Cloudflare域名无法访问")
        if not gunicorn_status:
            print("   - Gunicorn进程异常")

if __name__ == '__main__':
    main()
