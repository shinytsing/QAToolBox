#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻略生成功能测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_guide_generation():
    """测试攻略生成功能"""
    print("🎯 攻略生成功能测试")
    print("=" * 40)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 测试参数
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
        
        print("\n🚀 开始生成攻略...")
        
        # 生成攻略
        guide = service.get_travel_guide_data(
            destination=destination,
            travel_style=travel_style,
            budget_range=budget_range,
            travel_duration=travel_duration,
            interests=interests
        )
        
        print("✅ 攻略生成完成！")
        
        # 检查攻略内容
        print("\n📋 攻略内容检查:")
        
        # 检查基本信息
        print(f"  目的地: {guide.get('destination', 'N/A')}")
        print(f"  旅行风格: {guide.get('travel_style', 'N/A')}")
        print(f"  预算范围: {guide.get('budget_range', 'N/A')}")
        print(f"  旅行时长: {guide.get('travel_duration', 'N/A')}")
        
        # 检查景点
        attractions = guide.get('must_visit_attractions', [])
        print(f"  必玩景点: {attractions}")
        
        # 检查美食
        foods = guide.get('food_recommendations', [])
        print(f"  必吃美食: {foods}")
        
        # 检查贴士
        tips = guide.get('travel_tips', [])
        print(f"  旅行贴士: {tips}")
        
        # 检查每日行程
        daily_schedule = guide.get('daily_schedule', [])
        print(f"  每日行程数量: {len(daily_schedule)}")
        
        if daily_schedule:
            print("  每日行程详情:")
            for i, day in enumerate(daily_schedule, 1):
                print(f"    Day {i}: {day.get('date', 'N/A')}")
                print(f"      上午活动: {len(day.get('morning', []))} 个")
                print(f"      下午活动: {len(day.get('afternoon', []))} 个")
                print(f"      晚上活动: {len(day.get('evening', []))} 个")
        
        # 检查费用预算
        cost_breakdown = guide.get('cost_breakdown', {})
        print(f"  费用预算: {cost_breakdown.get('total_cost', 'N/A')}")
        
        # 验证结果
        print("\n📊 验证结果:")
        
        success = True
        
        if not attractions:
            print("  ❌ 景点信息为空")
            success = False
        else:
            print("  ✅ 景点信息正常")
        
        if not foods:
            print("  ❌ 美食信息为空")
            success = False
        else:
            print("  ✅ 美食信息正常")
        
        if not tips:
            print("  ❌ 旅行贴士为空")
            success = False
        else:
            print("  ✅ 旅行贴士正常")
        
        if not daily_schedule:
            print("  ❌ 每日行程为空")
            success = False
        else:
            print("  ✅ 每日行程正常")
        
        if not cost_breakdown:
            print("  ❌ 费用预算为空")
            success = False
        else:
            print("  ✅ 费用预算正常")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_daily_schedule_generation():
    """测试每日行程生成功能"""
    print("\n🗓️ 每日行程生成测试")
    print("=" * 30)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 测试数据
        test_data = {
            '景点': ['故宫博物院', '天安门广场', '颐和园'],
            '美食': ['北京烤鸭', '炸酱面', '豆汁']
        }
        
        print("测试数据:")
        print(f"  景点: {test_data['景点']}")
        print(f"  美食: {test_data['美食']}")
        
        # 生成3天行程
        schedule = service._generate_daily_schedule('北京', 3, test_data)
        
        print(f"\n生成的行程数量: {len(schedule)}")
        
        for i, day in enumerate(schedule, 1):
            print(f"\nDay {i}:")
            print(f"  上午: {len(day.get('morning', []))} 个活动")
            for activity in day.get('morning', []):
                print(f"    • {activity.get('time', '')} {activity.get('activity', '')}")
            
            print(f"  下午: {len(day.get('afternoon', []))} 个活动")
            for activity in day.get('afternoon', []):
                print(f"    • {activity.get('time', '')} {activity.get('activity', '')}")
            
            print(f"  晚上: {len(day.get('evening', []))} 个活动")
            for activity in day.get('evening', []):
                print(f"    • {activity.get('time', '')} {activity.get('activity', '')}")
        
        return len(schedule) > 0
        
    except Exception as e:
        print(f"❌ 每日行程生成测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🎯 攻略生成功能完整测试")
    print("=" * 50)
    
    # 测试攻略生成
    guide_test_passed = test_guide_generation()
    
    # 测试每日行程生成
    schedule_test_passed = test_daily_schedule_generation()
    
    print("\n" + "=" * 50)
    print("📊 最终测试结果")
    print("=" * 50)
    
    if guide_test_passed and schedule_test_passed:
        print("🎉 所有测试通过！攻略生成功能完全正常。")
    else:
        print("❌ 部分测试失败，请检查代码逻辑。")
        
        if not guide_test_passed:
            print("  - 攻略生成功能有问题")
        if not schedule_test_passed:
            print("  - 每日行程生成功能有问题")

if __name__ == "__main__":
    main() 