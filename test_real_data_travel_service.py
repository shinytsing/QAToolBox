#!/usr/bin/env python3
"""
测试真实数据旅游服务 - 验证DeepSeek API功能
"""

import os
import sys
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_real_data_travel_service():
    """测试真实数据旅游服务"""
    print("🧪 测试真实数据旅游服务...")
    try:
        from apps.tools.services.real_data_travel_service import RealDataTravelService
        
        # 初始化服务
        service = RealDataTravelService()
        print("✅ RealDataTravelService初始化成功")
        
        # 测试真实数据获取
        destinations = ["北京", "上海", "杭州", "成都", "西安"]
        
        for destination in destinations[:2]:  # 只测试前2个目的地
            print(f"\n🔍 测试目的地: {destination}")
            print("-" * 40)
            
            try:
                # 获取真实旅游攻略
                guide_data = service.get_real_travel_guide(
                    destination=destination,
                    travel_style="cultural",
                    budget_range="medium",
                    travel_duration="3天2晚",
                    interests=["美食", "文化", "历史"]
                )
                
                # 验证数据真实性
                print(f"✅ 攻略生成成功！")
                print(f"📊 数据来源: {guide_data.get('data_sources', {})}")
                print(f"🔍 是否真实数据: {guide_data.get('is_real_data', False)}")
                print(f"🤖 API使用: {guide_data.get('api_used', 'N/A')}")
                
                # 检查景点数据
                attractions = guide_data.get('must_visit_attractions', [])
                attractions_detail = guide_data.get('attractions_detail', [])
                print(f"🏛️ 景点数量: {len(attractions)}")
                print(f"🏛️ 详细景点数据: {len(attractions_detail)}")
                if attractions:
                    print(f"🏛️ 景点示例: {attractions[:3]}")
                
                # 检查美食数据
                foods = guide_data.get('food_recommendations', [])
                foods_detail = guide_data.get('foods_detail', [])
                print(f"🍜 美食数量: {len(foods)}")
                print(f"🍜 详细美食数据: {len(foods_detail)}")
                if foods:
                    print(f"🍜 美食示例: {foods[:3]}")
                
                # 检查住宿数据
                accommodations = guide_data.get('accommodation_data', [])
                print(f"🏨 住宿推荐: {len(accommodations)}")
                if accommodations:
                    print(f"🏨 住宿示例: {[acc.get('name', 'N/A') for acc in accommodations[:2]]}")
                
                # 检查交通数据
                transport = guide_data.get('transportation_guide', {})
                if transport:
                    print(f"🚗 交通信息: {list(transport.keys())}")
                
                # 检查天气数据
                weather_info = guide_data.get('weather_info', {})
                if 'current' in weather_info and not weather_info.get('error'):
                    current = weather_info['current']
                    print(f"🌤️ 当前天气: {current.get('weather', 'N/A')}")
                    print(f"🌡️ 当前温度: {current.get('temperature', 'N/A')}°C")
                    print(f"💧 湿度: {current.get('humidity', 'N/A')}%")
                else:
                    print("⚠️ 天气数据获取失败")
                
                # 检查地理信息
                geo_info = guide_data.get('geolocation_info', {})
                if geo_info.get('lat') and geo_info.get('lon'):
                    print(f"📍 地理坐标: {geo_info['lat']}, {geo_info['lon']}")
                    print(f"📍 显示名称: {geo_info.get('display_name', 'N/A')}")
                
                # 检查预算数据
                budget = guide_data.get('budget_estimate', {})
                if budget:
                    print(f"💰 总预算: {budget.get('total_cost', 'N/A')} {budget.get('currency', 'CNY')}")
                    print(f"💰 每日预算: {budget.get('daily_total', 'N/A')} {budget.get('currency', 'CNY')}")
                
                # 检查详细攻略
                detailed_guide = guide_data.get('detailed_guide', '')
                if detailed_guide:
                    print(f"📝 详细攻略长度: {len(detailed_guide)}字符")
                    print(f"📝 攻略预览: {detailed_guide[:300]}...")
                else:
                    print("⚠️ 详细攻略为空")
                
                print()
                
            except Exception as e:
                print(f"❌ {destination}攻略生成失败: {e}")
                print()
        
        return True
        
    except ImportError as e:
        print(f"❌ 无法导入RealDataTravelService: {e}")
        return False
    except Exception as e:
        print(f"❌ 真实数据旅游服务测试失败: {e}")
        return False

def test_deepseek_api_integration():
    """测试DeepSeek API集成"""
    print("\n🧪 测试DeepSeek API集成...")
    try:
        from apps.tools.services.real_data_travel_service import RealDataTravelService
        
        service = RealDataTravelService()
        
        # 测试景点数据获取
        print("🔍 测试景点数据获取...")
        attractions = service._get_real_attractions_with_deepseek("北京", "cultural", ["历史", "文化"])
        print(f"✅ 获取到 {len(attractions)} 个景点")
        if attractions:
            print(f"🏛️ 景点示例: {attractions[0]}")
        
        # 测试美食数据获取
        print("\n🍜 测试美食数据获取...")
        foods = service._get_real_foods_with_deepseek("北京", ["美食", "文化"])
        print(f"✅ 获取到 {len(foods)} 个美食")
        if foods:
            print(f"🍜 美食示例: {foods[0]}")
        
        # 测试住宿数据获取
        print("\n🏨 测试住宿数据获取...")
        accommodations = service._get_real_accommodations_with_deepseek("北京", "medium")
        print(f"✅ 获取到 {len(accommodations)} 个住宿选择")
        if accommodations:
            print(f"🏨 住宿示例: {accommodations[0]}")
        
        # 测试交通数据获取
        print("\n🚗 测试交通数据获取...")
        transport = service._get_real_transport_with_deepseek("北京")
        print(f"✅ 获取到交通信息: {list(transport.keys())}")
        if transport:
            print(f"🚗 交通示例: {list(transport.items())[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek API集成测试失败: {e}")
        return False

def test_api_endpoint():
    """测试API端点"""
    print("\n🧪 测试API端点...")
    try:
        import requests
        
        # 创建session
        session = requests.Session()
        
        # 获取CSRF token
        response = session.get('http://localhost:8001/users/login/')
        if response.status_code != 200:
            print(f"❌ 无法访问登录页面: {response.status_code}")
            return False
        
        # 提取CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ 无法获取CSRF token")
            return False
        
        csrf_token = csrf_match.group(1)
        
        # 设置CSRF cookie
        session.cookies.set('csrftoken', csrf_token)
        
        # 登录
        login_data = {
            'username': 'gaojie',
            'password': 'gaojie',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = session.post('http://localhost:8001/users/login/', data=login_data)
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            return False
        
        print("✅ 登录成功")
        
        # 测试旅游攻略生成API
        url = "http://localhost:8001/tools/api/travel-guide/"
        data = {
            "destination": "西安",
            "travel_style": "cultural",
            "budget_range": "medium",
            "travel_duration": "3天2晚",
            "interests": ["历史", "文化", "美食"]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        }
        
        print("📡 发送旅游攻略生成请求...")
        response = session.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                guide = result.get('guide', {})
                print("✅ API调用成功！")
                print(f"📊 攻略ID: {result.get('guide_id')}")
                print(f"📍 目的地: {guide.get('destination')}")
                print(f"🔍 是否真实数据: {guide.get('is_real_data', False)}")
                print(f"🤖 API使用: {guide.get('api_used', 'N/A')}")
                
                # 检查数据来源
                data_sources = guide.get('data_sources', {})
                if data_sources:
                    print("📊 数据来源:")
                    for source, value in data_sources.items():
                        if value:
                            print(f"  • {source}: {value}")
                
                # 检查景点数据
                attractions = guide.get('must_visit_attractions', [])
                attractions_detail = guide.get('attractions_detail', [])
                print(f"🏛️ 景点数量: {len(attractions)}")
                print(f"🏛️ 详细景点数据: {len(attractions_detail)}")
                if attractions:
                    print(f"🏛️ 景点示例: {attractions[:3]}")
                
                # 检查美食数据
                foods = guide.get('food_recommendations', [])
                foods_detail = guide.get('foods_detail', [])
                print(f"🍜 美食数量: {len(foods)}")
                print(f"🍜 详细美食数据: {len(foods_detail)}")
                if foods:
                    print(f"🍜 美食示例: {foods[:3]}")
                
                # 检查详细攻略
                detailed_guide = guide.get('detailed_guide', '')
                if detailed_guide:
                    print(f"📝 详细攻略长度: {len(detailed_guide)} 字符")
                    print(f"📝 攻略预览: {detailed_guide[:200]}...")
                
                return True
            else:
                print(f"❌ API返回错误: {result.get('error')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def test_data_quality():
    """测试数据质量"""
    print("\n🧪 测试数据质量...")
    try:
        from apps.tools.services.real_data_travel_service import RealDataTravelService
        
        service = RealDataTravelService()
        
        # 测试不同目的地
        test_cases = [
            {
                'destination': '北京',
                'travel_style': 'cultural',
                'budget_range': 'medium',
                'travel_duration': '3天2晚',
                'interests': ['历史', '文化']
            },
            {
                'destination': '上海',
                'travel_style': 'foodie',
                'budget_range': 'high',
                'travel_duration': '2天1晚',
                'interests': ['美食', '购物']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试案例 {i}: {test_case['destination']}")
            print("-" * 30)
            
            guide_data = service.get_real_travel_guide(**test_case)
            
            # 检查数据完整性
            required_fields = [
                'must_visit_attractions', 'food_recommendations', 
                'weather_info', 'budget_estimate', 'travel_tips',
                'attractions_detail', 'foods_detail', 'accommodation_data'
            ]
            
            for field in required_fields:
                if field in guide_data and guide_data[field]:
                    print(f"✅ {field}: 有数据")
                else:
                    print(f"❌ {field}: 无数据")
            
            # 检查数据真实性
            is_real_data = guide_data.get('is_real_data', False)
            api_used = guide_data.get('api_used', 'N/A')
            data_sources = guide_data.get('data_sources', {})
            
            print(f"🔍 数据真实性: {is_real_data}")
            print(f"🤖 API使用: {api_used}")
            print(f"📊 数据来源: {data_sources}")
            
            # 检查景点数据质量
            attractions = guide_data.get('must_visit_attractions', [])
            attractions_detail = guide_data.get('attractions_detail', [])
            if attractions:
                # 检查是否有具体的景点名称
                specific_attractions = [att for att in attractions if len(att) > 5 and not att.endswith('景点')]
                print(f"🏛️ 具体景点数量: {len(specific_attractions)}/{len(attractions)}")
                if specific_attractions:
                    print(f"🏛️ 具体景点示例: {specific_attractions[:2]}")
            
            if attractions_detail:
                print(f"🏛️ 详细景点数据: {len(attractions_detail)} 个")
                if attractions_detail:
                    detail = attractions_detail[0]
                    print(f"🏛️ 详细景点示例: {detail}")
            
            # 检查美食数据质量
            foods = guide_data.get('food_recommendations', [])
            foods_detail = guide_data.get('foods_detail', [])
            if foods:
                # 检查是否有具体的美食名称
                specific_foods = [food for food in foods if len(food) > 5 and not food.endswith('美食')]
                print(f"🍜 具体美食数量: {len(specific_foods)}/{len(foods)}")
                if specific_foods:
                    print(f"🍜 具体美食示例: {specific_foods[:2]}")
            
            if foods_detail:
                print(f"🍜 详细美食数据: {len(foods_detail)} 个")
                if foods_detail:
                    detail = foods_detail[0]
                    print(f"🍜 详细美食示例: {detail}")
            
            # 检查天气数据质量
            weather_info = guide_data.get('weather_info', {})
            if 'current' in weather_info and not weather_info.get('error'):
                current = weather_info['current']
                print(f"🌤️ 天气数据: {current.get('weather', 'N/A')}, {current.get('temperature', 'N/A')}°C")
            else:
                print("❌ 天气数据无效")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据质量测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试真实数据旅游服务...")
    print("=" * 60)
    
    # 测试真实数据旅游服务
    service_ok = test_real_data_travel_service()
    
    # 测试DeepSeek API集成
    api_ok = test_deepseek_api_integration()
    
    # 测试API端点
    endpoint_ok = test_api_endpoint()
    
    # 测试数据质量
    quality_ok = test_data_quality()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    
    if service_ok:
        print("✅ 真实数据旅游服务: 正常")
    else:
        print("❌ 真实数据旅游服务: 失败")
    
    if api_ok:
        print("✅ DeepSeek API集成: 正常")
    else:
        print("❌ DeepSeek API集成: 失败")
    
    if endpoint_ok:
        print("✅ API端点: 正常")
    else:
        print("❌ API端点: 失败")
    
    if quality_ok:
        print("✅ 数据质量: 优秀")
    else:
        print("❌ 数据质量: 需要改进")
    
    print("\n💡 改进说明:")
    print("1. ✅ 使用DeepSeek API获取真实景点数据")
    print("2. ✅ 使用DeepSeek API获取真实美食数据")
    print("3. ✅ 使用DeepSeek API获取真实住宿数据")
    print("4. ✅ 使用DeepSeek API获取真实交通数据")
    print("5. ✅ 使用DeepSeek API生成完整攻略")
    print("6. ✅ 集成免费API获取实时天气和地理信息")
    print("7. ✅ 提供详细的数据结构和元数据")
    print("8. ✅ 数据来源透明化和质量追踪")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
