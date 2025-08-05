#!/usr/bin/env python3
"""
前端心动链接测试脚本
模拟已登录用户的前端请求
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.contrib.auth import authenticate

def test_frontend_heart_link():
    """测试前端心动链接功能"""
    print("🎯 前端心动链接测试")
    print("="*50)
    
    # 创建测试用户
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ 使用现有用户: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='testpass123')
        print(f"✅ 创建测试用户: {user.username}")
    
    # 创建Django测试客户端
    client = Client()
    
    # 登录用户
    print(f"\n🔄 登录用户 {user.username}...")
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ 用户登录失败")
        return False
    
    print("✅ 用户登录成功")
    
    # 访问心动链接页面
    print(f"\n🔄 访问心动链接页面...")
    response = client.get('/tools/heart-link/')
    
    if response.status_code == 200:
        print("✅ 页面访问成功")
        print(f"📋 页面内容长度: {len(response.content)} 字符")
        
        # 检查页面是否包含CSRF token
        content = response.content.decode('utf-8')
        if 'csrfmiddlewaretoken' in content:
            print("✅ 页面包含CSRF token")
        else:
            print("❌ 页面不包含CSRF token")
            return False
        
        # 提取CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"✅ 提取到CSRF token: {csrf_token[:10]}...")
        else:
            print("❌ 无法提取CSRF token")
            return False
        
    else:
        print(f"❌ 页面访问失败: {response.status_code}")
        return False
    
    # 测试创建心动链接请求
    print(f"\n🔄 测试创建心动链接请求...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    response = client.post('/tools/api/heart-link/create/', 
                          data='{}',
                          content_type='application/json',
                          HTTP_X_CSRFTOKEN=csrf_token)
    
    print(f"📡 响应状态码: {response.status_code}")
    print(f"📋 响应内容: {response.content.decode('utf-8')}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode('utf-8'))
            print(f"✅ 请求成功: {data}")
            
            if data.get('success'):
                if data.get('matched'):
                    print("🎉 立即匹配成功！")
                else:
                    print("⏳ 等待匹配中...")
                    
                    # 测试状态检查
                    print(f"\n🔄 测试状态检查...")
                    status_response = client.get('/tools/api/heart-link/status/',
                                               HTTP_X_CSRFTOKEN=csrf_token)
                    
                    print(f"📡 状态检查响应: {status_response.status_code}")
                    print(f"📋 状态检查内容: {status_response.content.decode('utf-8')}")
                    
                    if status_response.status_code == 200:
                        status_data = json.loads(status_response.content.decode('utf-8'))
                        print(f"✅ 状态检查成功: {status_data}")
                    else:
                        print("❌ 状态检查失败")
                        
            else:
                print(f"❌ 请求失败: {data.get('error', '未知错误')}")
                return False
                
        except json.JSONDecodeError:
            print("❌ 响应不是有效的JSON格式")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False
    
    print(f"\n⏰ 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

def test_with_requests():
    """使用requests库测试（模拟真实浏览器）"""
    print("\n🌐 使用requests库测试")
    print("="*30)
    
    # 创建session
    session = requests.Session()
    
    # 访问登录页面获取CSRF token
    print("🔄 访问登录页面...")
    login_response = session.get('http://127.0.0.1:8002/users/login/')
    
    if login_response.status_code == 200:
        print("✅ 登录页面访问成功")
        
        # 提取CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"✅ 提取到CSRF token: {csrf_token[:10]}...")
            
            # 登录
            print("🔄 执行登录...")
            login_data = {
                'username': 'testuser',
                'password': 'testpass123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            login_result = session.post('http://127.0.0.1:8002/users/login/', data=login_data)
            
            if login_result.status_code == 200:
                print("✅ 登录成功")
                
                # 访问心动链接页面
                print("🔄 访问心动链接页面...")
                heart_link_response = session.get('http://127.0.0.1:8002/tools/heart-link/')
                
                if heart_link_response.status_code == 200:
                    print("✅ 心动链接页面访问成功")
                    
                    # 提取页面中的CSRF token
                    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', heart_link_response.text)
                    if csrf_match:
                        page_csrf_token = csrf_match.group(1)
                        print(f"✅ 页面CSRF token: {page_csrf_token[:10]}...")
                        
                        # 测试API请求
                        print("🔄 测试API请求...")
                        api_headers = {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': page_csrf_token
                        }
                        
                        api_response = session.post('http://127.0.0.1:8002/tools/api/heart-link/create/',
                                                  headers=api_headers,
                                                  json={})
                        
                        print(f"📡 API响应状态码: {api_response.status_code}")
                        print(f"📋 API响应内容: {api_response.text}")
                        
                        if api_response.status_code == 200:
                            print("✅ API请求成功！")
                            return True
                        else:
                            print("❌ API请求失败")
                            return False
                    else:
                        print("❌ 无法从页面提取CSRF token")
                        return False
                else:
                    print(f"❌ 心动链接页面访问失败: {heart_link_response.status_code}")
                    return False
            else:
                print(f"❌ 登录失败: {login_result.status_code}")
                return False
        else:
            print("❌ 无法从登录页面提取CSRF token")
            return False
    else:
        print(f"❌ 登录页面访问失败: {login_response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 开始前端心动链接测试")
    print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: Django测试客户端
    success1 = test_frontend_heart_link()
    
    # 测试2: requests库
    success2 = test_with_requests()
    
    print(f"\n{'='*50}")
    print("🏁 测试结果总结")
    print(f"{'='*50}")
    print(f"Django测试客户端: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"Requests库测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试都成功！前端心动链接功能正常工作！")
    else:
        print("❌ 部分测试失败，需要进一步调试。") 