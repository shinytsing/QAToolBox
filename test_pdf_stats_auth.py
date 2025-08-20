#!/usr/bin/env python3
"""
测试PDF转换器统计API（带认证）
"""

import os
import django
import requests
import json
from django.contrib.sessions.backends.db import SessionStore

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models.legacy_models import PDFConversionRecord

def test_pdf_stats_api_with_auth():
    """测试PDF统计API（带认证）"""
    print("🔍 测试PDF转换器统计API（带认证）...")
    
    # 获取用户
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到用户")
            return
        print(f"👤 使用用户: {user.username}")
    except Exception as e:
        print(f"❌ 用户检查失败: {str(e)}")
        return
    
    # 创建会话
    session = SessionStore()
    session['_auth_user_id'] = user.id
    session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
    session.save()
    
    print(f"🔑 会话ID: {session.session_key}")
    
    # 测试API调用
    try:
        print("🌐 测试API调用...")
        
        # 创建会话
        session_client = requests.Session()
        session_client.cookies.set('sessionid', session.session_key)
        
        response = session_client.get('http://localhost:8000/tools/api/pdf-converter/stats/')
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print(f"📄 响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API调用成功")
                print(f"📈 统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

if __name__ == '__main__':
    test_pdf_stats_api_with_auth()
