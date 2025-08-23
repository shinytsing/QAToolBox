#!/usr/bin/env python3
"""
详细测试社交媒体订阅通知API
"""

import requests
import json

def test_social_notifications_api():
    """测试社交媒体通知API"""
    base_url = "http://localhost:8000"
    
    # 测试获取通知列表API
    try:
        print("🧪 测试社交媒体订阅通知API...")
        print(f"请求URL: {base_url}/tools/api/social_subscription/notifications/")
        
        # 添加一些请求头
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(
            f"{base_url}/tools/api/social_subscription/notifications/",
            headers=headers,
            allow_redirects=False  # 不允许重定向
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容长度: {len(response.text)}")
        print(f"响应内容前500字符: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 成功解析JSON响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
        elif response.status_code == 302:
            print(f"🔄 重定向到: {response.headers.get('Location', 'Unknown')}")
        elif response.status_code == 401:
            print("🔒 需要认证")
        elif response.status_code == 403:
            print("🚫 权限不足")
        elif response.status_code == 500:
            print("💥 服务器内部错误")
            print(f"错误详情: {response.text}")
        else:
            print(f"❌ 其他错误状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_with_session():
    """测试带会话的请求"""
    base_url = "http://localhost:8000"
    
    try:
        print("\n🔐 测试带会话的请求...")
        
        session = requests.Session()
        
        # 首先访问主页获取CSRF token
        print("访问主页获取会话...")
        home_response = session.get(f"{base_url}/")
        print(f"主页状态码: {home_response.status_code}")
        
        # 尝试访问通知API
        print("访问通知API...")
        api_response = session.get(f"{base_url}/tools/api/social_subscription/notifications/")
        print(f"API状态码: {api_response.status_code}")
        print(f"API响应前500字符: {api_response.text[:500]}")
        
    except Exception as e:
        print(f"❌ 会话测试失败: {e}")

if __name__ == "__main__":
    test_social_notifications_api()
    test_with_session()
