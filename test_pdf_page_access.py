#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF转换器页面访问
"""

import requests

def test_pdf_page():
    """测试PDF转换器页面访问"""
    url = 'http://localhost:8000/tools/pdf_converter/'
    
    try:
        print(f"🔍 访问PDF转换器页面: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("✅ 页面访问成功")
            # 检查页面内容
            if 'PDF转换引擎' in response.text:
                print("✅ 页面内容正确")
                return True
            else:
                print("❌ 页面内容不正确")
                print(f"页面内容片段: {response.text[:200]}")
                return False
        elif response.status_code == 302:
            print("⚠️ 页面重定向")
            print(f"重定向到: {response.headers.get('Location')}")
            return False
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 页面访问出错: {e}")
        return False

def test_api_without_auth():
    """测试API无需认证"""
    url = 'http://localhost:8000/tools/api/pdf-converter/status/'
    
    try:
        print(f"\n🔍 测试API无需认证: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                print("✅ API返回JSON格式")
                try:
                    result = response.json()
                    print(f"API响应: {result}")
                    return True
                except:
                    print("❌ JSON解析失败")
                    return False
            else:
                print("❌ API返回非JSON格式")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API测试出错: {e}")
        return False

def test_main_page():
    """测试主页面"""
    url = 'http://localhost:8000/'
    
    try:
        print(f"\n🔍 测试主页面: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("✅ 主页面访问成功")
            return True
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 主页面测试出错: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PDF转换器页面访问测试")
    print("=" * 50)
    
    # 测试主页面
    main_success = test_main_page()
    
    # 测试PDF转换器页面
    pdf_page_success = test_pdf_page()
    
    # 测试API无需认证
    api_success = test_api_without_auth()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果")
    print("=" * 50)
    print(f"主页面: {'✅ 成功' if main_success else '❌ 失败'}")
    print(f"PDF页面: {'✅ 成功' if pdf_page_success else '❌ 失败'}")
    print(f"API无需认证: {'✅ 成功' if api_success else '❌ 失败'}")
    
    if main_success and pdf_page_success and api_success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
