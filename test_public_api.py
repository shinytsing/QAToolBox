#!/usr/bin/env python3
"""
测试公共API端点
"""

import requests
import json

def test_public_api():
    """测试公共API端点"""
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 测试公共API端点...")
        
        # 测试主页
        print("1. 测试主页...")
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        
        # 测试工具页面
        print("\n2. 测试工具页面...")
        response = requests.get(f"{base_url}/tools/")
        print(f"   状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        
        # 测试一个可能存在的公共API
        print("\n3. 测试可能的公共API...")
        response = requests.get(f"{base_url}/tools/api/")
        print(f"   状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        
        # 测试用户登录页面
        print("\n4. 测试用户登录页面...")
        response = requests.get(f"{base_url}/users/login/")
        print(f"   状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_public_api()
