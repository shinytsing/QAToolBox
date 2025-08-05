#!/usr/bin/env python3
"""
测试旅游攻略功能修复
- 验证行程不重复
- 验证导出功能正常
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
from apps.tools.models import TravelGuide
from apps.users.models import User

def test_daily_schedule_no_duplicates():
    """测试每日行程不重复"""
    print("🧪 测试每日行程不重复...")
    
    # 创建测试数据
    test_data = {
        'attractions': [
            {'name': '故宫', 'address': '北京市东城区', 'price': '60元', 'tips': '建议提前预约'},
            {'name': '天安门广场', 'address': '北京市东城区', 'price': '免费', 'tips': '注意安检'},
            {'name': '颐和园', 'address': '北京市海淀区', 'price': '30元', 'tips': '建议坐船游览'},
            {'name': '长城', 'address': '北京市延庆区', 'price': '40元', 'tips': '建议穿舒适鞋子'},
            {'name': '天坛', 'address': '北京市东城区', 'price': '15元', 'tips': '早上人少'},
            {'name': '北海公园', 'address': '北京市西城区', 'price': '10元', 'tips': '可以划船'}
        ],
        'restaurants': [
            {'name': '全聚德烤鸭', 'address': '北京市东城区', 'price_range': '100-200元', 'specialty': '北京烤鸭'},
            {'name': '东来顺', 'address': '北京市西城区', 'price_range': '80-150元', 'specialty': '涮羊肉'},
            {'name': '护国寺小吃', 'address': '北京市西城区', 'price_range': '20-50元', 'specialty': '老北京小吃'},
            {'name': '南锣鼓巷美食', 'address': '北京市东城区', 'price_range': '30-80元', 'specialty': '特色小吃'}
        ],
        'accommodation': [
            {'name': '北京饭店', 'address': '北京市东城区', 'price_range': '800-1500元', 'recommendation': '位置优越'},
            {'name': '如家酒店', 'address': '北京市西城区', 'price_range': '200-400元', 'recommendation': '性价比高'},
            {'name': '北京国际青年旅舍', 'address': '北京市朝阳区', 'price_range': '100-200元', 'recommendation': '适合背包客'}
        ]
    }
    
    # 创建服务实例
    service = TravelDataService()
    
    # 生成4天的行程
    daily_schedule = service._generate_daily_schedule('北京', 4, test_data)
    
    # 检查循环使用是否正确
    expected_attractions = ['故宫', '天安门广场', '颐和园', '长城', '天坛', '北海公园']
    expected_restaurants = ['全聚德烤鸭', '东来顺', '护国寺小吃', '南锣鼓巷美食']
    expected_hotels = ['北京饭店', '如家酒店', '北京国际青年旅舍']
    
    actual_attractions = []
    actual_restaurants = []
    actual_hotels = []
    
    for day in daily_schedule:
        print(f"\n📅 第{day['day']}天:")
        
        # 收集景点
        for time_slot in ['morning', 'afternoon']:
            for activity in day[time_slot]:
                attraction_name = activity['activity'].replace('游览', '')
                actual_attractions.append(attraction_name)
                print(f"  ✅ {activity['time']}: {activity['activity']}")
        
        # 收集餐厅
        for activity in day['evening']:
            restaurant_name = activity['activity'].replace('在', '').replace('用餐', '')
            actual_restaurants.append(restaurant_name)
            print(f"  ✅ {activity['time']}: {activity['activity']}")
        
        # 收集酒店
        if day['accommodation']:
            actual_hotels.append(day['accommodation'])
            print(f"  ✅ 住宿: {day['accommodation']}")
    
    # 验证循环使用是否正确
    print(f"\n📊 验证结果:")
    print(f"景点使用顺序: {actual_attractions}")
    print(f"餐厅使用顺序: {actual_restaurants}")
    print(f"酒店使用顺序: {actual_hotels}")
    
    # 检查是否有不合理的重复（连续重复）
    for i in range(1, len(actual_attractions)):
        if actual_attractions[i] == actual_attractions[i-1]:
            print(f"❌ 景点连续重复: {actual_attractions[i]}")
            return False
    
    for i in range(1, len(actual_restaurants)):
        if actual_restaurants[i] == actual_restaurants[i-1]:
            print(f"❌ 餐厅连续重复: {actual_restaurants[i]}")
            return False
    
    for i in range(1, len(actual_hotels)):
        if actual_hotels[i] == actual_hotels[i-1]:
            print(f"❌ 酒店连续重复: {actual_hotels[i]}")
            return False
    
    print("\n✅ 循环使用正确，没有连续重复！")
    return True

def test_export_functionality():
    """测试导出功能"""
    print("\n🧪 测试导出功能...")
    
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='test_travel_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # 创建测试攻略
        guide = TravelGuide.objects.create(
            user=user,
            destination='北京',
            travel_style='文化探索',
            budget_range='中等预算',
            travel_duration='4天3晚',
            interests=['历史', '文化', '美食'],
            must_visit_attractions=['故宫', '天安门广场', '颐和园'],
            food_recommendations=['北京烤鸭', '涮羊肉', '老北京小吃'],
            transportation_guide={
                '地铁': '北京地铁四通八达，建议购买交通卡',
                '公交': '公交车线路覆盖广泛，票价便宜',
                '出租车': '起步价13元，建议使用滴滴打车'
            },
            budget_estimate={
                '住宿': '800元/晚',
                '餐饮': '200元/天',
                '交通': '50元/天',
                '门票': '150元/天'
            },
            travel_tips=[
                '建议提前预约热门景点',
                '注意天气变化，准备合适衣物',
                '保管好随身物品，注意安全'
            ],
            best_time_to_visit='春秋两季，气候宜人',
            daily_schedule=[
                {
                    'day': 1,
                    'date': '第1天',
                    'morning': [
                        {
                            'time': '09:00-12:00',
                            'activity': '游览故宫',
                            'location': '北京市东城区',
                            'cost': '60元',
                            'tips': '建议提前预约'
                        }
                    ],
                    'afternoon': [
                        {
                            'time': '14:00-17:00',
                            'activity': '游览天安门广场',
                            'location': '北京市东城区',
                            'cost': '免费',
                            'tips': '注意安检'
                        }
                    ],
                    'evening': [
                        {
                            'time': '18:00-20:00',
                            'activity': '在全聚德烤鸭用餐',
                            'location': '北京市东城区',
                            'cost': '100-200元',
                            'tips': '推荐品尝北京烤鸭'
                        }
                    ],
                    'night': [],
                    'accommodation': '北京饭店',
                    'total_cost': 320
                }
            ],
            cost_breakdown={
                'total_cost': 2000,
                'accommodation': {'total_cost': 800, 'daily_cost': 200},
                'food': {'total_cost': 600, 'daily_cost': 150},
                'transport': {'total_cost': 200, 'daily_cost': 50},
                'attractions': {'total_cost': 400, 'daily_cost': 100}
            }
        )
        
        print(f"✅ 创建测试攻略成功，ID: {guide.id}")
        
        # 测试格式化函数
        from apps.tools.views import format_travel_guide_for_export
        formatted_content = format_travel_guide_for_export(guide)
        
        if formatted_content:
            print("✅ 格式化内容生成成功")
            print(f"内容长度: {len(formatted_content)} 字符")
        else:
            print("❌ 格式化内容生成失败")
            return False
        
        # 清理测试数据
        guide.delete()
        user.delete()
        
        print("✅ 导出功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 导出功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试旅游攻略功能修复...")
    print("=" * 50)
    
    # 测试行程不重复
    schedule_test_passed = test_daily_schedule_no_duplicates()
    
    # 测试导出功能
    export_test_passed = test_export_functionality()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"  行程不重复测试: {'✅ 通过' if schedule_test_passed else '❌ 失败'}")
    print(f"  导出功能测试: {'✅ 通过' if export_test_passed else '❌ 失败'}")
    
    if schedule_test_passed and export_test_passed:
        print("\n🎉 所有测试都通过了！")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查代码")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 