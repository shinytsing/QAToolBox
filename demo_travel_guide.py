#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能旅游攻略生成引擎 - 演示脚本
展示完整的旅游攻略生成功能
"""

import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def demo_travel_guide():
    """演示智能旅游攻略生成功能"""
    print("🎯 智能旅游攻略生成引擎 - 功能演示")
    print("=" * 60)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        # 创建服务实例
        service = TravelDataService()
        
        # 演示参数
        destination = "北京"
        travel_style = "文化探索"
        budget_range = "中等预算"
        travel_duration = "3天"
        interests = ["历史古迹", "美食", "文化体验"]
        
        print(f"📍 目的地: {destination}")
        print(f"🎭 旅行风格: {travel_style}")
        print(f"💰 预算范围: {budget_range}")
        print(f"⏰ 旅行时长: {travel_duration}")
        print(f"🎯 兴趣偏好: {', '.join(interests)}")
        
        print("\n🚀 开始生成智能攻略...")
        print("=" * 60)
        
        # 调用智能攻略生成引擎
        guide = service.get_travel_guide_data(
            destination=destination,
            travel_style=travel_style,
            budget_range=budget_range,
            travel_duration=travel_duration,
            interests=interests
        )
        
        # 展示结果
        print("\n📋 生成的攻略内容:")
        print("=" * 60)
        
        if 'title' in guide:
            print(f"📖 {guide['title']}")
            print()
        
        if 'daily_schedule' in guide:
            print("🗓️ 每日行程安排:")
            for i, day in enumerate(guide['daily_schedule'], 1):
                print(f"  Day {i}: {day.get('date', f'第{i}天')}")
                
                # 显示上午行程
                if day.get('morning'):
                    print("    上午:")
                    for activity in day['morning']:
                        print(f"      • {activity.get('time', '')} {activity.get('activity', '')}")
                
                # 显示下午行程
                if day.get('afternoon'):
                    print("    下午:")
                    for activity in day['afternoon']:
                        print(f"      • {activity.get('time', '')} {activity.get('activity', '')}")
                
                # 显示晚上行程
                if day.get('evening'):
                    print("    晚上:")
                    for activity in day['evening']:
                        print(f"      • {activity.get('time', '')} {activity.get('activity', '')}")
                
                print()
        
        if 'top_attractions' in guide:
            print("🏆 必玩景点:")
            for i, attraction in enumerate(guide['top_attractions'], 1):
                print(f"  {i}. {attraction}")
            print()
        
        if 'must_eat_foods' in guide:
            print("🍜 必吃美食:")
            for i, food in enumerate(guide['must_eat_foods'], 1):
                print(f"  {i}. {food}")
            print()
        
        if 'travel_tips' in guide and guide['travel_tips']:
            print("💡 旅行贴士:")
            for i, tip in enumerate(guide['travel_tips'], 1):
                print(f"  {i}. {tip}")
            print()
        elif 'travel_tips' in guide:
            print("💡 旅行贴士: 暂无")
            print()
        
        if 'cost_breakdown' in guide:
            print("💰 费用预算:")
            cost = guide['cost_breakdown']
            
            # 处理不同的费用格式
            if isinstance(cost.get('accommodation'), dict):
                print(f"  住宿: ¥{cost['accommodation'].get('total_cost', 0)}")
            else:
                print(f"  住宿: ¥{cost.get('accommodation', 0)}")
                
            if isinstance(cost.get('food'), dict):
                print(f"  餐饮: ¥{cost['food'].get('total_cost', 0)}")
            else:
                print(f"  餐饮: ¥{cost.get('food', 0)}")
                
            if isinstance(cost.get('transport'), dict):
                print(f"  交通: ¥{cost['transport'].get('total_cost', 0)}")
            else:
                print(f"  交通: ¥{cost.get('transportation', 0)}")
                
            if isinstance(cost.get('attractions'), dict):
                print(f"  门票: ¥{cost['attractions'].get('total_cost', 0)}")
            else:
                print(f"  门票: ¥{cost.get('tickets', 0)}")
                
            print(f"  总计: ¥{cost.get('total_cost', 0)}")
            print()
        
        if 'weather_info' in guide:
            print("🌤️ 天气信息:")
            weather = guide['weather_info']
            print(f"  温度: {weather.get('temperature', '')}°C")
            print(f"  天气: {weather.get('weather', '')}")
            print(f"  湿度: {weather.get('humidity', '')}%")
            print()
        
        print("✅ 攻略生成完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("请确保已安装所有依赖包")
        return False
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        return False

def demo_info_extraction():
    """演示信息提取功能"""
    print("\n🔧 信息提取功能演示")
    print("=" * 40)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 测试文本
        test_texts = [
            "推荐景点：故宫博物院、天安门广场、颐和园 必吃：北京烤鸭、炸酱面、豆汁 注意：避开节假日高峰，提前预约门票",
            "推荐景点：西湖、灵隐寺、雷峰塔 必吃：龙井虾仁、东坡肉、叫化鸡 注意：春季赏花最佳，夏季注意防暑",
            "推荐景点：外滩、豫园、东方明珠 必吃：小笼包、生煎包、红烧肉 注意：地铁出行方便，注意钱包安全"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 测试文本 {i}:")
            print(f"  {text}")
            
            result = service.提取核心信息(text)
            
            print(f"🔍 提取结果:")
            print(f"  景点: {result['景点']}")
            print(f"  美食: {result['美食']}")
            print(f"  贴士: {result['贴士']}")
        
        print("\n✅ 信息提取功能演示完成！")
        return True
        
    except Exception as e:
        print(f"❌ 信息提取演示失败: {str(e)}")
        return False

def check_api_status():
    """检查API状态"""
    print("\n🔍 API状态检查")
    print("=" * 30)
    
    apis = {
        'DEEPSEEK_API_KEY': 'DeepSeek API',
        'GOOGLE_API_KEY': 'Google API',
        'GOOGLE_CSE_ID': 'Google Custom Search Engine ID',
        'OPENWEATHER_API_KEY': 'OpenWeatherMap API'
    }
    
    all_configured = True
    
    for key, name in apis.items():
        value = os.getenv(key)
        if value and 'your-' not in value:
            print(f"✅ {name}: 已配置")
        else:
            print(f"❌ {name}: 未配置")
            all_configured = False
    
    if not all_configured:
        print("\n💡 部分API未配置，将使用模拟数据生成攻略")
        print("建议运行 python setup_travel_apis.py 配置完整API")
    
    return all_configured

def main():
    """主函数"""
    print("🎯 智能旅游攻略生成引擎 - 完整演示")
    print("=" * 60)
    
    # 检查API状态
    api_configured = check_api_status()
    
    # 演示信息提取功能
    demo_info_extraction()
    
    # 演示完整攻略生成
    success = demo_travel_guide()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 演示完成！智能旅游攻略生成引擎运行正常。")
        
        if not api_configured:
            print("\n💡 提示：")
            print("1. 配置完整API可获得更准确的攻略数据")
            print("2. 运行 python setup_travel_apis.py 配置API")
            print("3. 运行 python test_travel_apis.py 测试API")
    else:
        print("❌ 演示失败，请检查错误信息并修复问题。")

if __name__ == "__main__":
    main() 