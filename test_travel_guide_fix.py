#!/usr/bin/env python3
"""
旅游指南功能修复测试脚本
"""

import os
import sys
import django
import json
import requests

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.tools.models import TravelGuide
from apps.tools.services.travel_data_service import TravelDataService

def test_travel_data_service():
    """测试旅游数据服务"""
    print("🧪 测试旅游数据服务...")
    
    try:
        service = TravelDataService()
        
        # 测试北京数据
        print("  📍 测试北京数据...")
        beijing_data = service.get_travel_guide_data(
            destination="北京",
            travel_style="cultural",
            budget_range="medium",
            travel_duration="3-5天",
            interests=["文化", "历史"]
        )
        
        print(f"     ✅ 北京数据获取成功")
        print(f"     景点数量: {len(beijing_data.get('must_visit_attractions', []))}")
        print(f"     美食数量: {len(beijing_data.get('food_recommendations', []))}")
        
        # 测试上海数据
        print("  📍 测试上海数据...")
        shanghai_data = service.get_travel_guide_data(
            destination="上海",
            travel_style="leisure",
            budget_range="luxury",
            travel_duration="1周",
            interests=["美食", "购物"]
        )
        
        print(f"     ✅ 上海数据获取成功")
        print(f"     景点数量: {len(shanghai_data.get('must_visit_attractions', []))}")
        print(f"     美食数量: {len(shanghai_data.get('food_recommendations', []))}")
        
        # 测试重庆数据
        print("  📍 测试重庆数据...")
        chongqing_data = service.get_travel_guide_data(
            destination="重庆",
            travel_style="foodie",
            budget_range="budget",
            travel_duration="1-2天",
            interests=["美食", "自然"]
        )
        
        print(f"     ✅ 重庆数据获取成功")
        print(f"     景点数量: {len(chongqing_data.get('must_visit_attractions', []))}")
        print(f"     美食数量: {len(chongqing_data.get('food_recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"     ❌ 旅游数据服务测试失败: {str(e)}")
        return False

def test_travel_guide_api():
    """测试旅游指南API"""
    print("🧪 测试旅游指南API...")
    
    try:
        client = Client()
        
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        # 登录用户
        client.login(username='test_user', password='testpass123')
        
        # 测试生成攻略API
        print("  📝 测试生成攻略API...")
        response = client.post('/tools/api/travel-guide/', {
            'destination': '北京',
            'travel_style': 'cultural',
            'budget_range': 'medium',
            'travel_duration': '3-5天',
            'interests': ['文化', '历史']
        }, content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"     ✅ 生成攻略API测试成功")
                print(f"     攻略ID: {data.get('guide_id')}")
                print(f"     目的地: {data.get('guide', {}).get('destination')}")
            else:
                print(f"     ❌ 生成攻略API返回错误: {data.get('error')}")
                return False
        else:
            print(f"     ❌ 生成攻略API请求失败: {response.status_code}")
            return False
        
        # 测试获取攻略列表API
        print("  📋 测试获取攻略列表API...")
        response = client.get('/tools/api/travel-guide/list/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                guides = data.get('guides', [])
                print(f"     ✅ 获取攻略列表API测试成功")
                print(f"     攻略数量: {len(guides)}")
            else:
                print(f"     ❌ 获取攻略列表API返回错误: {data.get('error')}")
                return False
        else:
            print(f"     ❌ 获取攻略列表API请求失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"     ❌ 旅游指南API测试失败: {str(e)}")
        return False

def test_travel_guide_model():
    """测试旅游指南模型"""
    print("🧪 测试旅游指南模型...")
    
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='test_user_model',
            defaults={'email': 'test_model@example.com'}
        )
        
        # 创建测试攻略
        guide = TravelGuide.objects.create(
            user=user,
            destination="测试城市",
            travel_style="general",
            budget_range="medium",
            travel_duration="3-5天",
            interests=["美食", "文化"],
            must_visit_attractions=["测试景点1", "测试景点2"],
            food_recommendations=["测试餐厅1", "测试餐厅2"],
            transportation_guide={"飞机": "测试交通信息"},
            weather_info={"春季": "测试天气信息"},
            best_time_to_visit="春秋季节",
            budget_estimate={"经济型": "2000-3000元"},
            travel_tips=["测试贴士1", "测试贴士2"]
        )
        
        print(f"     ✅ 旅游指南模型创建成功")
        print(f"     攻略ID: {guide.id}")
        print(f"     目的地: {guide.destination}")
        print(f"     景点数量: {guide.get_attractions_count()}")
        print(f"     美食数量: {guide.get_food_count()}")
        
        # 清理测试数据
        guide.delete()
        print(f"     ✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"     ❌ 旅游指南模型测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始旅游指南功能修复测试...")
    print("=" * 50)
    
    tests = [
        ("旅游数据服务", test_travel_data_service),
        ("旅游指南模型", test_travel_guide_model),
        ("旅游指南API", test_travel_guide_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！旅游指南功能修复成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 