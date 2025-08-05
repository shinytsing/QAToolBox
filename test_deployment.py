#!/usr/bin/env python3
"""
QAToolBox 部署测试脚本
用于测试部署是否成功
"""

import requests
import time
import sys
from datetime import datetime

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def test_health_check(server_url):
    """测试健康检查"""
    try:
        log(f"测试健康检查: {server_url}/health/")
        response = requests.get(f"{server_url}/health/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ 健康检查通过: {data}")
            return True
        else:
            log(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"❌ 健康检查异常: {e}")
        return False

def test_home_page(server_url):
    """测试首页"""
    try:
        log(f"测试首页: {server_url}")
        response = requests.get(server_url, timeout=10)
        
        if response.status_code == 200:
            log("✅ 首页访问成功")
            return True
        else:
            log(f"❌ 首页访问失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"❌ 首页访问异常: {e}")
        return False

def test_admin_page(server_url):
    """测试管理员页面"""
    try:
        log(f"测试管理员页面: {server_url}/admin/")
        response = requests.get(f"{server_url}/admin/", timeout=10)
        
        if response.status_code == 200:
            log("✅ 管理员页面访问成功")
            return True
        else:
            log(f"❌ 管理员页面访问失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"❌ 管理员页面访问异常: {e}")
        return False

def test_static_files(server_url):
    """测试静态文件"""
    try:
        log(f"测试静态文件: {server_url}/static/")
        response = requests.get(f"{server_url}/static/", timeout=10)
        
        if response.status_code == 200:
            log("✅ 静态文件访问成功")
            return True
        else:
            log(f"❌ 静态文件访问失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"❌ 静态文件访问异常: {e}")
        return False

def main():
    """主函数"""
    server_url = "http://47.103.143.152"
    
    log("开始部署测试...")
    log(f"测试服务器: {server_url}")
    
    # 等待服务启动
    log("等待服务启动...")
    time.sleep(15)
    
    tests = [
        ("健康检查", lambda: test_health_check(server_url)),
        ("首页", lambda: test_home_page(server_url)),
        ("管理员页面", lambda: test_admin_page(server_url)),
        ("静态文件", lambda: test_static_files(server_url)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        log(f"\n--- 测试 {test_name} ---")
        if test_func():
            passed += 1
        time.sleep(2)  # 测试间隔
    
    log(f"\n=== 测试结果 ===")
    log(f"通过: {passed}/{total}")
    
    if passed == total:
        log("🎉 所有测试通过！部署成功！")
        log(f"🌐 访问地址: {server_url}")
        log("👤 管理员账号: admin")
        log("🔑 管理员密码: admin123456")
        return 0
    else:
        log("⚠️  部分测试失败，请检查部署状态")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 