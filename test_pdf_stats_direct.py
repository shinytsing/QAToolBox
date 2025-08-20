#!/usr/bin/env python3
"""
直接测试PDF转换器统计API视图函数
"""

import os
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from apps.tools.views.pdf_converter_views import pdf_converter_stats_api

def test_pdf_stats_direct():
    """直接测试PDF统计API视图函数"""
    print("🔍 直接测试PDF转换器统计API视图函数...")
    
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
    
    # 创建请求
    factory = RequestFactory()
    request = factory.get('/tools/api/pdf-converter/stats/')
    request.user = user
    
    # 调用视图函数
    try:
        print("🔧 调用视图函数...")
        response = pdf_converter_stats_api(request)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.content.decode()[:500]}...")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content.decode())
                print("✅ 视图函数调用成功")
                print(f"📈 统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON")
        else:
            print(f"❌ 视图函数调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 视图函数测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pdf_stats_direct()
