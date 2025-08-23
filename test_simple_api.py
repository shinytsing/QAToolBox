#!/usr/bin/env python3
"""
测试简单API结构
"""

import requests
import json

def test_simple_api():
    """测试简单API结构"""
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 测试简单API结构...")
        
        # 测试一个可能存在的简单API端点
        test_endpoints = [
            "/tools/",
            "/tools/api/",
            "/users/",
            "/admin/",
            "/api/",
        ]
        
        for endpoint in test_endpoints:
            print(f"\n测试端点: {endpoint}")
            try:
                response = requests.get(f"{base_url}{endpoint}")
                print(f"   状态码: {response.status_code}")
                print(f"   内容类型: {response.headers.get('Content-Type', 'Unknown')}")
                
                if response.status_code == 200:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        print("   ✅ 返回JSON")
                    elif 'text/html' in response.headers.get('Content-Type', ''):
                        print("   📄 返回HTML")
                    else:
                        print(f"   ❓ 其他内容类型")
                elif response.status_code == 302:
                    print(f"   🔄 重定向到: {response.headers.get('Location', 'Unknown')}")
                elif response.status_code == 404:
                    print("   ❌ 404 未找到")
                else:
                    print(f"   ❓ 其他状态码")
                    
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_simple_api()
