#!/usr/bin/env python3
"""
测试PDF转换器统计API
"""

import os
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models.legacy_models import PDFConversionRecord

def test_pdf_stats_api():
    """测试PDF统计API"""
    print("🔍 测试PDF转换器统计API...")
    
    # 检查模型是否存在
    try:
        print("📋 检查PDFConversionRecord模型...")
        count = PDFConversionRecord.objects.count()
        print(f"✅ 模型正常，当前记录数: {count}")
    except Exception as e:
        print(f"❌ 模型检查失败: {str(e)}")
        return
    
    # 检查是否有用户
    try:
        user = User.objects.first()
        if user:
            print(f"👤 使用用户: {user.username}")
        else:
            print("❌ 没有找到用户")
            return
    except Exception as e:
        print(f"❌ 用户检查失败: {str(e)}")
        return
    
    # 测试API调用
    try:
        print("🌐 测试API调用...")
        response = requests.get('http://localhost:8000/tools/api/pdf-converter/stats/', 
                              cookies={'sessionid': 'test'})
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"📈 统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

if __name__ == '__main__':
    test_pdf_stats_api()
