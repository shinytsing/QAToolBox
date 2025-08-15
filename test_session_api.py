#!/usr/bin/env python3
"""
测试session-status API的脚本
"""

import requests
import json

def test_session_status_api():
    """测试session-status API"""
    base_url = "http://127.0.0.1:8000"
    api_url = f"{base_url}/users/api/session-status/"
    
    print("=== 测试session-status API ===")
    print(f"API URL: {api_url}")
    
    try:
        # 测试未登录状态
        print("\n1. 测试未登录状态:")
        response = requests.get(api_url)
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 401:
            try:
                data = response.json()
                print(f"JSON解析成功: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        
        # 测试登录状态（需要先登录）
        print("\n2. 测试登录状态:")
        print("请先手动登录，然后运行以下命令:")
        print(f"curl -H 'Cookie: sessionid=YOUR_SESSION_ID' {api_url}")
        
    except requests.exceptions.ConnectionError:
        print("连接失败，请确保Django服务器正在运行")
    except Exception as e:
        print(f"测试失败: {e}")

def test_with_session_cookie():
    """使用session cookie测试"""
    base_url = "http://127.0.0.1:8000"
    api_url = f"{base_url}/users/api/session-status/"
    
    print("\n=== 使用session cookie测试 ===")
    
    # 这里需要替换为实际的session ID
    session_id = input("请输入您的session ID (从浏览器开发者工具获取): ").strip()
    
    if session_id:
        cookies = {'sessionid': session_id}
        try:
            response = requests.get(api_url, cookies=cookies)
            print(f"状态码: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON解析成功: {data}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
        except Exception as e:
            print(f"测试失败: {e}")
    else:
        print("未提供session ID，跳过测试")

if __name__ == "__main__":
    test_session_status_api()
    test_with_session_cookie()
