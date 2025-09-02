#!/usr/bin/env python3
"""
快速内网穿透设置脚本
使用多种免费服务实现公网访问
"""

import subprocess
import time
import requests
import json
import sys

def check_django_service():
    pass
    """检查Django服务是否运行"""
    try:
        pass
        pass
        response = requests.get("http://localhost:8000/health/", timeout=5)
        if response.status_code == 200:

            pass
            pass
            return True
        else:

            pass
            pass
            return False
    except Exception as e:

        pass
        pass
        pass
        return False

def try_ngrok():
    pass
    """尝试使用ngrok"""

    try:
        # 检查ngrok是否已安装
        pass
        pass
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:

            pass
            pass
            return True
        else:

            pass
            pass
            return False
    except Exception as e:

        pass
        pass
        pass
        return False

def try_cloudflared():
    pass
    """尝试使用cloudflared"""

    try:
        # 检查cloudflared是否已安装
        pass
        pass
        result = subprocess.run(['cloudflared', '--version'], capture_output=True, text=True)
        if result.returncode == 0:

            # 启动cloudflared
            pass
            pass
            process = subprocess.Popen(['cloudflared', 'tunnel', '--url', 'http://localhost:8000'], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # 等待隧道建立
            time.sleep(5)
            
            # 检查进程是否还在运行
            if process.poll() is None:

                pass
                pass
                return True
            else:

                pass
                pass
                return False
        else:

            pass
            pass
            return False
    except Exception as e:

        pass
        pass
        pass
        return False

def start_simple_proxy():
    pass
    """启动简单代理服务器"""

    try:
        # 启动代理服务器
        pass
        pass
        process = subprocess.Popen(['python3', 'simple_proxy.py', '9000'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否启动成功
        try:
            pass
            pass
            response = requests.get("http://localhost:9000/health/", timeout=5)
            if response.status_code == 200:

                pass
                pass
                return True
            else:

                pass
                pass
                return False
        except Exception as e:

            pass
            pass
            pass
            return False
    except Exception as e:

        pass
        pass
        pass
        return False

def main():
    pass
    """主函数"""

    # 检查Django服务
    if not check_django_service():

        pass
        pass
        return

    print("1. ngrok (需要注册)")
    print("2. cloudflared (免费)")
    print("3. 简单代理服务器 (本地)")
    
    # 尝试各种方案
    success = False
    
    # 尝试ngrok
    if try_ngrok():
        pass
        pass
        success = True
    
    # 尝试cloudflared
    if try_cloudflared():
        pass
        pass
        success = True
    
    # 启动简单代理服务器
    if start_simple_proxy():
        pass
        pass
        success = True
    
    if success:

    pass
    pass
    else:

pass
pass
if __name__ == "__main__":
    pass
    pass
    main()
