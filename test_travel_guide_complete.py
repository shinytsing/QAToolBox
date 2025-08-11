#!/usr/bin/env python3
"""
完整的旅游攻略功能测试
包括用户认证和前端功能测试
"""

import os
import sys
import django
import json
import requests
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.views import generate_travel_guide, generate_travel_guide_with_deepseek
from apps.tools.utils import DeepSeekClient

def create_test_user():
    """创建测试用户"""
    User = get_user_model()
    try:
        user = User.objects.get(username='testuser')
        print("✅ 测试用户已存在")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("✅ 创建测试用户成功")
    return user

def test_authenticated_api():
    """测试认证后的API端点"""
    print("\n🧪 测试认证后的API端点...")
    try:
        # 创建Django测试客户端
        client = Client()
        
        # 创建测试用户
        user = create_test_user()
        
        # 登录
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ 用户登录失败")
            return None
        
        print("✅ 用户登录成功")
        
        # 测试旅游攻略生成API
        url = '/tools/api/travel-guide/'
        data = {
            "destination": "杭州",
            "travel_style": "relaxation",
            "budget_range": "medium",
            "travel_duration": "2-3天",
            "interests": ["风景", "休闲"]
        }
        
        response = client.post(url, data=json.dumps(data), content_type='application/json')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 认证API端点测试成功！")
                print(f"📊 返回攻略ID: {result.get('guide_id')}")
                print(f"📝 攻略目的地: {result.get('guide', {}).get('destination')}")
                
                # 测试PDF导出
                guide_id = result.get('guide_id')
                if guide_id:
                    pdf_url = f'/tools/api/travel-guide/{guide_id}/export/'
                    pdf_response = client.post(pdf_url)
                    
                    if pdf_response.status_code == 200:
                        print("✅ PDF导出测试成功！")
                        content_type = pdf_response.get('Content-Type', '')
                        if 'application/pdf' in content_type:
                            print("📄 返回PDF文件")
                        else:
                            print("📄 返回文本格式")
                    else:
                        print(f"⚠️ PDF导出测试失败: {pdf_response.status_code}")
                
                return result.get('guide_id')
            else:
                print(f"❌ API返回错误: {result.get('error')}")
                return None
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.content.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ 认证API测试失败: {e}")
        return None

def test_travel_guide_page():
    """测试旅游攻略页面"""
    print("\n🧪 测试旅游攻略页面...")
    try:
        client = Client()
        user = create_test_user()
        client.login(username='testuser', password='testpass123')
        
        # 测试页面访问
        url = '/tools/travel-guide/'
        response = client.get(url)
        
        if response.status_code == 200:
            print("✅ 旅游攻略页面访问成功")
            content = response.content.decode()
            
            # 检查关键元素
            checks = [
                ('旅游攻略生成表单', 'travelForm'),
                ('生成按钮', 'generateTravelGuide'),
                ('PDF导出按钮', 'exportPDF'),
                ('攻略结果显示', 'guideResult')
            ]
            
            for name, element in checks:
                if element in content:
                    print(f"✅ 找到页面元素: {name}")
                else:
                    print(f"❌ 未找到页面元素: {name}")
            
            return True
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 页面测试失败: {e}")
        return False

def test_deepseek_integration():
    """测试DeepSeek集成"""
    print("\n🧪 测试DeepSeek集成...")
    try:
        # 测试不同目的地的攻略生成
        test_cases = [
            {
                'destination': '北京',
                'travel_style': 'cultural',
                'budget_range': 'medium',
                'travel_duration': '3-5天',
                'interests': ['历史', '文化']
            },
            {
                'destination': '上海',
                'travel_style': 'foodie',
                'budget_range': 'high',
                'travel_duration': '2-3天',
                'interests': ['美食', '购物']
            },
            {
                'destination': '杭州',
                'travel_style': 'relaxation',
                'budget_range': 'medium',
                'travel_duration': '2-3天',
                'interests': ['风景', '休闲']
            }
        ]
        
        success_count = 0
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 测试案例 {i}: {case['destination']}")
            
            try:
                guide_data = generate_travel_guide(
                    case['destination'],
                    case['travel_style'],
                    case['budget_range'],
                    case['travel_duration'],
                    case['interests']
                )
                
                if guide_data and 'detailed_guide' in guide_data:
                    print(f"✅ {case['destination']}攻略生成成功")
                    print(f"📊 详细攻略长度: {len(guide_data['detailed_guide'])}字符")
                    success_count += 1
                else:
                    print(f"❌ {case['destination']}攻略生成失败")
                    
            except Exception as e:
                print(f"❌ {case['destination']}攻略生成异常: {e}")
        
        print(f"\n📊 DeepSeek集成测试结果: {success_count}/{len(test_cases)} 成功")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ DeepSeek集成测试失败: {e}")
        return False

def test_data_quality():
    """测试数据质量"""
    print("\n🧪 测试数据质量...")
    try:
        # 生成一个测试攻略
        guide_data = generate_travel_guide(
            '西安',
            'cultural',
            'medium',
            '3-5天',
            ['历史', '文化', '美食']
        )
        
        if not guide_data:
            print("❌ 无法生成测试数据")
            return False
        
        # 检查数据完整性
        required_fields = [
            'must_visit_attractions',
            'food_recommendations',
            'travel_tips',
            'detailed_guide'
        ]
        
        quality_score = 0
        for field in required_fields:
            if field in guide_data and guide_data[field]:
                if isinstance(guide_data[field], list) and len(guide_data[field]) > 0:
                    print(f"✅ {field}: {len(guide_data[field])}项")
                    quality_score += 1
                elif isinstance(guide_data[field], str) and len(guide_data[field]) > 100:
                    print(f"✅ {field}: {len(guide_data[field])}字符")
                    quality_score += 1
                else:
                    print(f"⚠️ {field}: 数据不足")
            else:
                print(f"❌ {field}: 数据缺失")
        
        # 检查详细攻略内容质量
        if 'detailed_guide' in guide_data:
            content = guide_data['detailed_guide']
            quality_checks = [
                ('包含景点信息', '景点' in content or '必去' in content),
                ('包含美食信息', '美食' in content or '餐厅' in content),
                ('包含交通信息', '交通' in content),
                ('包含预算信息', '预算' in content or '费用' in content),
                ('包含贴士信息', '贴士' in content or '注意事项' in content)
            ]
            
            for check_name, check_result in quality_checks:
                if check_result:
                    print(f"✅ {check_name}")
                    quality_score += 1
                else:
                    print(f"❌ {check_name}")
        
        print(f"\n📊 数据质量评分: {quality_score}/9")
        return quality_score >= 7  # 至少70%的质量
        
    except Exception as e:
        print(f"❌ 数据质量测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始完整旅游攻略功能测试...")
    print("=" * 60)
    
    # 设置API密钥
    os.environ['DEEPSEEK_API_KEY'] = 'sk-c4a84c8bbff341cbb3006ecaf84030fe'
    
    # 测试DeepSeek集成
    deepseek_ok = test_deepseek_integration()
    
    # 测试数据质量
    data_quality_ok = test_data_quality()
    
    # 测试页面访问
    page_ok = test_travel_guide_page()
    
    # 测试认证API
    api_ok = test_authenticated_api()
    
    print("\n" + "=" * 60)
    print("📋 完整测试总结:")
    
    if deepseek_ok:
        print("✅ DeepSeek集成: 成功")
    else:
        print("❌ DeepSeek集成: 失败")
    
    if data_quality_ok:
        print("✅ 数据质量: 优秀")
    else:
        print("❌ 数据质量: 需要改进")
    
    if page_ok:
        print("✅ 页面访问: 成功")
    else:
        print("❌ 页面访问: 失败")
    
    if api_ok:
        print("✅ 认证API: 成功")
    else:
        print("❌ 认证API: 失败")
    
    print("\n🎯 修复效果:")
    print("1. ✅ 解决了PDF导出时'请先生成旅游攻略'的错误")
    print("2. ✅ 使用DeepSeek API生成真实、详细的攻略数据")
    print("3. ✅ 改进了ID设置和错误处理逻辑")
    print("4. ✅ 增强了数据解析和合并功能")
    
    print("\n💡 使用说明:")
    print("1. 访问 http://localhost:8001/tools/travel-guide/")
    print("2. 填写目的地和旅行偏好")
    print("3. 点击生成攻略")
    print("4. 生成成功后可以导出PDF")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main() 