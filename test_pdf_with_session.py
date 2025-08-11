#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带会话的PDF转换测试
"""

import os
import sys
import requests
import tempfile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def get_csrf_token():
    """获取CSRF令牌"""
    try:
        # 获取登录页面以获取CSRF令牌
        session = requests.Session()
        response = session.get('http://localhost:8000/accounts/login/', timeout=10)
        
        if response.status_code == 200:
            # 从HTML中提取CSRF令牌
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ 获取到CSRF令牌: {csrf_token[:20]}...")
                return session, csrf_token
        
        print("❌ 无法获取CSRF令牌")
        return session, None
        
    except Exception as e:
        print(f"❌ 获取CSRF令牌失败: {e}")
        return None, None

def test_text_to_pdf_with_session():
    """使用会话测试文本转PDF"""
    session, csrf_token = get_csrf_token()
    if not session:
        return False
    
    url = 'http://localhost:8000/tools/api/pdf-converter/'
    
    data = {
        'type': 'text-to-pdf',
        'text_content': 'This is a test text for PDF conversion.'
    }
    
    headers = {}
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
        data['csrfmiddlewaretoken'] = csrf_token
    
    try:
        print("🧪 测试文本转PDF（带会话）...")
        response = session.post(url, data=data, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"JSON响应: {result}")
                
                if result.get('success'):
                    print("✅ 文本转PDF成功!")
                    download_url = result.get('download_url')
                    if download_url:
                        print(f"下载链接: {download_url}")
                        
                        # 测试下载
                        download_response = session.get(f"http://localhost:8000{download_url}", timeout=30)
                        if download_response.status_code == 200:
                            print(f"✅ 下载成功! 文件大小: {len(download_response.content)} 字节")
                            return True
                        else:
                            print(f"❌ 下载失败: {download_response.status_code}")
                            return False
                    else:
                        print("⚠️ 没有下载链接")
                        return True
                else:
                    print(f"❌ 转换失败: {result.get('error')}")
                    return False
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_direct_api_call():
    """直接测试API调用"""
    url = 'http://localhost:8000/tools/api/pdf-converter/'
    
    # 创建一个简单的测试请求
    data = {
        'type': 'text-to-pdf',
        'text_content': 'Test content'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        print("🧪 直接API调用测试...")
        response = requests.post(url, data=data, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    result = response.json()
                    print(f"✅ JSON响应: {result}")
                    return True
                except Exception as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:200]}")
                    return False
            else:
                print(f"❌ 响应不是JSON格式")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_status_api():
    """测试状态API"""
    url = 'http://localhost:8000/tools/api/pdf-converter/status/'
    
    headers = {
        'Accept': 'application/json'
    }
    
    try:
        print("🧪 测试状态API...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    result = response.json()
                    print(f"✅ 状态API响应: {result}")
                    return True
                except Exception as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:200]}")
                    return False
            else:
                print(f"❌ 状态API响应不是JSON格式")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 状态API请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 状态API测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 带会话的PDF转换测试")
    print("=" * 50)
    
    # 测试状态API
    print("\n1️⃣ 测试状态API")
    status_success = test_status_api()
    
    # 测试直接API调用
    print("\n2️⃣ 测试直接API调用")
    direct_success = test_direct_api_call()
    
    # 测试带会话的转换
    print("\n3️⃣ 测试带会话的文本转PDF")
    session_success = test_text_to_pdf_with_session()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果")
    print("=" * 50)
    print(f"状态API: {'✅ 成功' if status_success else '❌ 失败'}")
    print(f"直接API调用: {'✅ 成功' if direct_success else '❌ 失败'}")
    print(f"带会话转换: {'✅ 成功' if session_success else '❌ 失败'}")
    
    if status_success and direct_success and session_success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
