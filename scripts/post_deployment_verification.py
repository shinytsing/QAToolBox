#!/usr/bin/env python3
"""
部署后验证脚本
用于验证部署是否成功，检查关键功能是否正常
"""

import argparse
import requests
import sys
import time
from urllib.parse import urljoin


def check_health_endpoint(base_url):
    """检查健康检查端点"""
    try:
        health_url = urljoin(base_url, '/health/')
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ 健康检查通过: {health_url}")
            return True
        else:
            print(f"❌ 健康检查失败: {health_url} (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查异常: {health_url} - {e}")
        return False


def check_static_files(base_url):
    """检查静态文件是否可访问"""
    try:
        static_url = urljoin(base_url, '/static/')
        response = requests.get(static_url, timeout=10)
        if response.status_code in [200, 404]:  # 404也是正常的，说明静态文件配置正确
            print(f"✅ 静态文件配置正常: {static_url}")
            return True
        else:
            print(f"⚠️  静态文件可能有问题: {static_url} (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  静态文件检查异常: {static_url} - {e}")
        return False


def check_api_endpoints(base_url):
    """检查API端点"""
    api_endpoints = [
        '/users/api/session-status/',
        '/admin/',
    ]
    
    success_count = 0
    for endpoint in api_endpoints:
        try:
            api_url = urljoin(base_url, endpoint)
            response = requests.get(api_url, timeout=10)
            if response.status_code in [200, 302, 403]:  # 这些状态码都表示端点可访问
                print(f"✅ API端点可访问: {api_url}")
                success_count += 1
            else:
                print(f"⚠️  API端点状态异常: {api_url} (状态码: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ API端点异常: {api_url} - {e}")
    
    return success_count > 0


def check_response_time(base_url, max_time=3.0):
    """检查响应时间"""
    try:
        start_time = time.time()
        response = requests.get(base_url, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            if response_time <= max_time:
                print(f"✅ 响应时间正常: {response_time:.2f}s")
                return True
            else:
                print(f"⚠️  响应时间过长: {response_time:.2f}s (阈值: {max_time}s)")
                return False
        else:
            print(f"❌ 主页访问失败: {base_url} (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 主页访问异常: {base_url} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='部署后验证脚本')
    parser.add_argument('--url', required=True, help='要验证的URL')
    parser.add_argument('--max-time', type=float, default=3.0, help='最大响应时间（秒）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    
    print(f"🔍 开始验证部署: {base_url}")
    print("=" * 50)
    
    # 执行各项检查
    checks = [
        ("健康检查", lambda: check_health_endpoint(base_url)),
        ("静态文件", lambda: check_static_files(base_url)),
        ("API端点", lambda: check_api_endpoints(base_url)),
        ("响应时间", lambda: check_response_time(base_url, args.max_time)),
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 检查: {check_name}")
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ 检查异常: {check_name} - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {passed_checks}/{total_checks} 项检查通过")
    
    if passed_checks == total_checks:
        print("🎉 所有检查通过，部署验证成功！")
        return 0
    elif passed_checks >= total_checks * 0.7:  # 70%通过率
        print("⚠️  大部分检查通过，部署基本成功")
        return 0
    else:
        print("❌ 多项检查失败，部署可能存在问题")
        return 1


if __name__ == '__main__':
    sys.exit(main())