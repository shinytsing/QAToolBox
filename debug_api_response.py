#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试API响应内容
"""

import requests

def debug_api_response():
    """调试API响应"""
    url = 'http://localhost:8000/tools/api/pdf-converter/status/'
    
    try:
        print(f"🔍 请求URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"\n📄 响应内容 (前500字符):")
        content = response.text[:500]
        print(content)
        
        print(f"\n🔢 响应内容长度: {len(response.text)}")
        
        # 尝试解析JSON
        try:
            json_data = response.json()
            print(f"✅ JSON解析成功")
            print(f"📋 JSON内容: {json_data}")
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    debug_api_response()
