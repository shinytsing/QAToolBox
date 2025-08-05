#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试武汉旅游数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.travel_data_service import TravelDataService

def test_wuhan_data_direct():
    """直接测试武汉数据"""
    print("🧪 直接测试武汉旅游数据")
    print("=" * 50)
    
    travel_service = TravelDataService()
    
    # 直接测试各个数据获取函数
    print("1. 测试景点数据获取...")
    attractions_data = travel_service._get_attractions_data("武汉")
    print(f"景点数据: {attractions_data}")
    print()
    
    print("2. 测试美食数据获取...")
    food_data = travel_service._get_food_data("武汉")
    print(f"美食数据: {food_data}")
    print()
    
    print("3. 测试住宿数据获取...")
    accommodation_data = travel_service._get_accommodation_data("武汉")
    print(f"住宿数据: {accommodation_data}")
    print()
    
    print("4. 测试真实数据获取...")
    real_data = travel_service._get_real_travel_data("武汉")
    print(f"真实数据: {real_data}")
    print()
    
    print("5. 测试完整攻略生成...")
    guide_data = travel_service.get_travel_guide_data(
        destination="武汉",
        travel_style="general",
        budget_range="medium",
        travel_duration="3-5天",
        interests=["文化", "美食"]
    )
    print(f"攻略数据: {guide_data}")
    print()
    
    # 检查详细攻略
    if 'detailed_guide' in guide_data:
        print("📝 生成的详细攻略:")
        print("-" * 30)
        print(guide_data['detailed_guide'])
        print()

if __name__ == '__main__':
    test_wuhan_data_direct() 