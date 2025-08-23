#!/usr/bin/env python3
"""
测试带登录的API
"""

import requests
import json

def test_with_login():
    """测试带登录的API"""
    base_url = "http://localhost:8000"
    
    try:
        print("🔐 测试带登录的API...")
        
        session = requests.Session()
        
        # 1. 访问登录页面获取CSRF token
        print("1. 获取登录页面和CSRF token...")
        login_response = session.get(f"{base_url}/users/login/")
        print(f"   登录页面状态码: {login_response.status_code}")
        
        # 从HTML中提取CSRF token
        csrf_token = None
        if 'csrf-token' in login_response.text:
            import re
            match = re.search(r'content="([^"]+)"', login_response.text)
            if match:
                csrf_token = match.group(1)
                print(f"   找到CSRF token: {csrf_token[:20]}...")
        
        if not csrf_token:
            print("   ❌ 未找到CSRF token")
            return
        
        # 2. 尝试登录（使用一个测试用户）
        print("\n2. 尝试登录...")
        login_data = {
            'username': 'test_user',  # 使用一个测试用户名
            'password': 'test_password',  # 使用一个测试密码
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_headers = {
            'Referer': f"{base_url}/users/login/",
            'X-CSRFToken': csrf_token
        }
        
        login_result = session.post(
            f"{base_url}/users/login/",
            data=login_data,
            headers=login_headers
        )
        
        print(f"   登录结果状态码: {login_result.status_code}")
        print(f"   登录后重定向到: {login_result.url if hasattr(login_result, 'url') else 'None'}")
        
        # 3. 测试API
        print("\n3. 测试通知API...")
        api_response = session.get(
            f"{base_url}/tools/api/social_subscription/notifications/",
            headers={'Accept': 'application/json'}
        )
        
        print(f"   API状态码: {api_response.status_code}")
        print(f"   API内容类型: {api_response.headers.get('Content-Type', 'Unknown')}")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print(f"   ✅ 成功获取JSON响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"   ❌ JSON解析失败，响应内容: {api_response.text[:200]}...")
        else:
            print(f"   ❌ API请求失败，响应: {api_response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_with_login()
