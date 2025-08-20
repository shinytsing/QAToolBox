#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF统计前端显示
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_pdf_stats_direct():
    """直接测试PDF统计API视图函数"""
    print("🔍 直接测试PDF统计API视图函数...")
    
    try:
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from apps.tools.views.pdf_converter_views import pdf_converter_stats_api
        
        # 获取用户
        user = User.objects.first()
        if not user:
            print("❌ 没有找到用户")
            return False
        
        # 创建请求
        factory = RequestFactory()
        request = factory.get('/tools/api/pdf-converter/stats/')
        request.user = user
        
        # 调用视图函数
        response = pdf_converter_stats_api(request)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content.decode())
            if data.get('success'):
                stats = data['stats']
                print("✅ 视图函数调用成功")
                print(f"📈 统计数据:")
                print(f"   总转换次数: {stats['total_conversions']}")
                print(f"   处理文件数: {stats['total_files']}")
                print(f"   平均转换时间: {stats['average_speed']}s")
                print(f"   用户满意度: {stats['user_satisfaction']}%")
                print(f"   最近转换记录数: {len(stats['recent_conversions'])}")
                
                # 验证数据合理性
                print("\n🔍 数据验证:")
                if stats['total_conversions'] == stats['total_files']:
                    print("✅ 总转换次数与处理文件数一致")
                else:
                    print("❌ 总转换次数与处理文件数不一致")
                
                if 0 <= stats['user_satisfaction'] <= 100:
                    print("✅ 用户满意度在合理范围内")
                else:
                    print("❌ 用户满意度超出合理范围")
                
                if stats['average_speed'] >= 0:
                    print("✅ 平均转换时间合理")
                else:
                    print("❌ 平均转换时间不合理")
                
                return True
            else:
                print(f"❌ 视图函数返回错误: {data.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ 视图函数调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 直接测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始测试PDF统计功能...")
    success = test_pdf_stats_direct()
    if success:
        print("\n🎉 测试通过！PDF统计功能正常工作")
    else:
        print("\n⚠️ 测试失败，请检查相关功能")
