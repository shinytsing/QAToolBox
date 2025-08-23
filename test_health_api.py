#!/usr/bin/env python3
"""
测试健康检查API
"""

import requests
import json

def test_health_api():
    """测试健康检查API"""
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 测试健康检查API...")
        
        # 测试健康检查端点
        response = requests.get(f"{base_url}/health/")
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 成功获取JSON响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
        else:
            print(f"❌ 请求失败，响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_health_api()
