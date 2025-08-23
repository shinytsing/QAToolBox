#!/usr/bin/env python3
"""
测试社交媒体订阅通知API
"""

import requests
import json

def test_social_notifications_api():
    """测试社交媒体通知API"""
    base_url = "http://localhost:8000"
    
    # 测试获取通知列表API
    try:
        response = requests.get(f"{base_url}/tools/api/social_subscription/notifications/")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🧪 测试社交媒体订阅通知API...")
    test_social_notifications_api()
