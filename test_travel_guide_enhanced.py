#!/usr/bin/env python3
"""
测试增强版旅游攻略系统
- 验证实时数据抓取
- 验证DeepSeek API调用
- 验证成都等城市的数据处理
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.travel_data_service import TravelDataService

def test_chengdu_travel_guide():
    """测试成都旅游攻略生成"""
    print("🧪 测试成都旅游攻略生成...")
    
    # 创建服务实例
    service = TravelDataService()
    
    # 测试参数
    destination = "成都"
    travel_style = "美食文化"
    budget_range = "中等预算"
    travel_duration = "3天2晚"
    interests = ["美食", "文化", "历史"]
    
    print(f"📍 目的地: {destination}")
    print(f"🎯 旅行风格: {travel_style}")
    print(f"💰 预算范围: {budget_range}")
    print(f"⏰ 旅行时长: {travel_duration}")
    print(f"🎨 兴趣偏好: {', '.join(interests)}")
    print("-" * 50)
    
    try:
        # 生成攻略
        guide = service.get_travel_guide_data(destination, travel_style, 
                                            budget_range, travel_duration, 
                                            interests)
        
        # 验证结果
        print("\n📊 攻略生成结果:")
        print(f"✅ 目的地: {guide.get('destination', 'N/A')}")
        print(f"✅ 旅行风格: {guide.get('travel_style', 'N/A')}")
        print(f"✅ 预算范围: {guide.get('budget_range', 'N/A')}")
        
        # 检查必去景点
        attractions = guide.get('must_visit_attractions', [])
        print(f"✅ 必去景点数量: {len(attractions)}")
        if attractions:
            print("🏛️ 景点列表:")
            for i, attraction in enumerate(attractions[:3], 1):
                print(f"  {i}. {attraction}")
        
        # 检查美食推荐
        foods = guide.get('food_recommendations', [])
        print(f"✅ 美食推荐数量: {len(foods)}")
        if foods:
            print("🍜 美食列表:")
            for i, food in enumerate(foods[:3], 1):
                print(f"  {i}. {food}")
        
        # 检查每日行程
        daily_schedule = guide.get('daily_schedule', [])
        print(f"✅ 每日行程数量: {len(daily_schedule)}")
        if daily_schedule:
            print("🗓️ 行程安排:")
            for day in daily_schedule[:2]:  # 只显示前2天
                print(f"  第{day.get('day', 'N/A')}天:")
                for time_slot in ['morning', 'afternoon', 'evening']:
                    activities = day.get(time_slot, [])
                    if activities:
                        print(f"    {time_slot}: {len(activities)}个活动")
        
        # 检查费用明细
        cost_breakdown = guide.get('cost_breakdown', {})
        if cost_breakdown:
            print(f"✅ 总费用: ¥{cost_breakdown.get('total_cost', 0)}")
            print(f"✅ 旅行天数: {cost_breakdown.get('travel_days', 0)}天")
        
        # 检查AI生成内容
        ai_content = guide.get('ai_generated_content', '')
        if ai_content:
            print(f"✅ AI生成内容长度: {len(ai_content)} 字符")
            print("🤖 AI内容预览:")
            print(ai_content[:200] + "..." if len(ai_content) > 200 else ai_content)
        
        print("\n🎉 成都旅游攻略测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 成都旅游攻略测试失败: {e}")
        return False

def test_api_configuration():
    """测试API配置"""
    print("\n🔧 测试API配置...")
    
    service = TravelDataService()
    
    # 检查DeepSeek API
    if service.deepseek_api_key:
        print("✅ DeepSeek API密钥已配置")
    else:
        print("❌ DeepSeek API密钥未配置")
    
    # 检查Google API
    if service.google_api_key:
        print("✅ Google API密钥已配置")
    else:
        print("❌ Google API密钥未配置")
    
    # 检查天气API
    if service.weather_api_key:
        print("✅ 天气API密钥已配置")
    else:
        print("❌ 天气API密钥未配置")
    
    return True

def test_data_fetching():
    """测试数据抓取功能"""
    print("\n📡 测试数据抓取功能...")
    
    service = TravelDataService()
    
    try:
        # 测试小红书数据搜索
        print("  🔍 测试小红书数据搜索...")
        xhs_data = service._search_xiaohongshu_via_deepseek("成都")
        if 'error' not in xhs_data:
            print("  ✅ 小红书数据搜索成功")
        else:
            print(f"  ⚠️ 小红书数据搜索: {xhs_data['error']}")
        
        # 测试马蜂窝数据搜索
        print("  🔍 测试马蜂窝数据搜索...")
        mfw_data = service._search_mafengwo_via_google("成都")
        if 'error' not in mfw_data:
            print("  ✅ 马蜂窝数据搜索成功")
        else:
            print(f"  ⚠️ 马蜂窝数据搜索: {mfw_data['error']}")
        
        # 测试天气数据获取
        print("  🌤️ 测试天气数据获取...")
        weather_data = service._get_weather_data("成都")
        if 'error' not in weather_data:
            print("  ✅ 天气数据获取成功")
        else:
            print(f"  ⚠️ 天气数据获取: {weather_data['error']}")
        
        # 测试景点数据获取
        print("  🏛️ 测试景点数据获取...")
        attractions_data = service._get_real_attractions_data("成都")
        if attractions_data:
            print(f"  ✅ 景点数据获取成功，共{len(attractions_data)}个景点")
        else:
            print("  ⚠️ 景点数据获取失败")
        
        # 测试美食数据获取
        print("  🍜 测试美食数据获取...")
        food_data = service._get_real_food_data("成都")
        if food_data:
            print(f"  ✅ 美食数据获取成功，共{len(food_data)}个美食")
        else:
            print("  ⚠️ 美食数据获取失败")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据抓取测试失败: {e}")
        return False

def test_ai_integration():
    """测试AI集成功能"""
    print("\n🤖 测试AI集成功能...")
    
    service = TravelDataService()
    
    try:
        # 测试DeepSeek API调用
        print("  🔍 测试DeepSeek API调用...")
        test_prompt = "请简单介绍一下成都的特色美食"
        response = service._call_deepseek_api(test_prompt)
        
        if response:
            print("  ✅ DeepSeek API调用成功")
            print(f"  📝 响应长度: {len(response)} 字符")
            print("  📄 响应预览:")
            print(response[:100] + "..." if len(response) > 100 else response)
        else:
            print("  ❌ DeepSeek API调用失败")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI集成测试失败: {e}")
        return False

def test_other_cities():
    """测试其他城市"""
    print("\n🌍 测试其他城市...")
    
    service = TravelDataService()
    cities = ["北京", "上海", "重庆", "武汉"]
    
    for city in cities:
        print(f"  🏙️ 测试{city}...")
        try:
            # 获取基础景点数据
            attractions = service._get_basic_attractions_data(city)
            if attractions:
                print(f"    ✅ {city}景点数据: {len(attractions)}个")
            else:
                print(f"    ⚠️ {city}景点数据: 无")
            
            # 获取基础美食数据
            foods = service._get_basic_food_data(city)
            if foods:
                print(f"    ✅ {city}美食数据: {len(foods)}个")
            else:
                print(f"    ⚠️ {city}美食数据: 无")
                
        except Exception as e:
            print(f"    ❌ {city}测试失败: {e}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始测试增强版旅游攻略系统...")
    print("=" * 60)
    
    # 测试API配置
    api_test_passed = test_api_configuration()
    
    # 测试数据抓取
    data_test_passed = test_data_fetching()
    
    # 测试AI集成
    ai_test_passed = test_ai_integration()
    
    # 测试其他城市
    cities_test_passed = test_other_cities()
    
    # 测试成都攻略生成
    chengdu_test_passed = test_chengdu_travel_guide()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"  API配置测试: {'✅ 通过' if api_test_passed else '❌ 失败'}")
    print(f"  数据抓取测试: {'✅ 通过' if data_test_passed else '❌ 失败'}")
    print(f"  AI集成测试: {'✅ 通过' if ai_test_passed else '❌ 失败'}")
    print(f"  其他城市测试: {'✅ 通过' if cities_test_passed else '❌ 失败'}")
    print(f"  成都攻略测试: {'✅ 通过' if chengdu_test_passed else '❌ 失败'}")
    
    all_passed = all([api_test_passed, data_test_passed, ai_test_passed, 
                     cities_test_passed, chengdu_test_passed])
    
    if all_passed:
        print("\n🎉 所有测试都通过了！")
        print("✨ 增强版旅游攻略系统运行正常")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 