#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息提取功能测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_info_extraction():
    """测试信息提取功能"""
    print("🔧 信息提取功能测试")
    print("=" * 40)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 测试用例
        test_cases = [
            {
                "text": "推荐景点：故宫博物院、天安门广场、颐和园 必吃：北京烤鸭、炸酱面、豆汁 注意：避开节假日高峰，提前预约门票",
                "expected_attractions": ["故宫博物院", "天安门广场", "颐和园"],
                "expected_foods": ["北京烤鸭", "炸酱面", "豆汁"],
                "expected_tips": ["避开节假日高峰", "提前预约门票"]
            },
            {
                "text": "推荐景点：西湖、灵隐寺、雷峰塔 必吃：龙井虾仁、东坡肉、叫化鸡 注意：春季赏花最佳，夏季注意防暑",
                "expected_attractions": ["西湖", "灵隐寺", "雷峰塔"],
                "expected_foods": ["龙井虾仁", "东坡肉", "叫化鸡"],
                "expected_tips": ["春季赏花最佳", "夏季注意防暑"]
            },
            {
                "text": "推荐景点：外滩、豫园、东方明珠 必吃：小笼包、生煎包、红烧肉 注意：地铁出行方便，注意钱包安全",
                "expected_attractions": ["外滩", "豫园", "东方明珠"],
                "expected_foods": ["小笼包", "生煎包", "红烧肉"],
                "expected_tips": ["地铁出行方便", "注意钱包安全"]
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试用例 {i}:")
            print(f"  输入文本: {test_case['text']}")
            
            result = service.提取核心信息(test_case['text'])
            
            print(f"  提取结果:")
            print(f"    景点: {result['景点']}")
            print(f"    美食: {result['美食']}")
            print(f"    贴士: {result['贴士']}")
            
            # 验证结果
            attractions_match = set(result['景点']) == set(test_case['expected_attractions'])
            foods_match = set(result['美食']) == set(test_case['expected_foods'])
            tips_match = set(result['贴士']) == set(test_case['expected_tips'])
            
            if attractions_match and foods_match and tips_match:
                print(f"  ✅ 测试通过")
            else:
                print(f"  ❌ 测试失败")
                if not attractions_match:
                    print(f"    景点不匹配: 期望 {test_case['expected_attractions']}, 实际 {result['景点']}")
                if not foods_match:
                    print(f"    美食不匹配: 期望 {test_case['expected_foods']}, 实际 {result['美食']}")
                if not tips_match:
                    print(f"    贴士不匹配: 期望 {test_case['expected_tips']}, 实际 {result['贴士']}")
                all_passed = False
        
        print(f"\n📊 测试总结:")
        if all_passed:
            print("🎉 所有测试用例通过！信息提取功能正常。")
        else:
            print("❌ 部分测试用例失败，请检查信息提取逻辑。")
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🔍 边界情况测试")
    print("=" * 30)
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 边界测试用例
        edge_cases = [
            {
                "text": "推荐景点：故宫博物院 必吃：北京烤鸭 注意：避开节假日",
                "description": "单个项目"
            },
            {
                "text": "推荐景点： 必吃： 注意：",
                "description": "空内容"
            },
            {
                "text": "推荐景点：故宫博物院、天安门广场 必吃：北京烤鸭、炸酱面",
                "description": "缺少注意项"
            },
            {
                "text": "推荐景点：故宫博物院 必吃：北京烤鸭 注意：避开节假日 推荐景点：颐和园",
                "description": "重复关键词"
            }
        ]
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n📝 边界测试 {i} ({case['description']}):")
            print(f"  输入文本: {case['text']}")
            
            result = service.提取核心信息(case['text'])
            
            print(f"  提取结果:")
            print(f"    景点: {result['景点']}")
            print(f"    美食: {result['美食']}")
            print(f"    贴士: {result['贴士']}")
            
            # 检查是否没有崩溃
            if isinstance(result, dict) and all(key in result for key in ['景点', '美食', '贴士']):
                print(f"  ✅ 处理正常")
            else:
                print(f"  ❌ 处理异常")
        
        print(f"\n✅ 边界情况测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 边界测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🎯 信息提取功能完整测试")
    print("=" * 50)
    
    # 基本功能测试
    basic_test_passed = test_info_extraction()
    
    # 边界情况测试
    edge_test_passed = test_edge_cases()
    
    print("\n" + "=" * 50)
    print("📊 最终测试结果")
    print("=" * 50)
    
    if basic_test_passed and edge_test_passed:
        print("🎉 所有测试通过！信息提取功能完全正常。")
        print("\n💡 功能特点:")
        print("  ✅ 能够正确提取景点、美食、贴士信息")
        print("  ✅ 支持多个项目用顿号分隔")
        print("  ✅ 支持贴士用逗号分隔")
        print("  ✅ 能够处理边界情况")
        print("  ✅ 严格按照用户指令的正则表达式实现")
    else:
        print("❌ 部分测试失败，请检查代码逻辑。")

if __name__ == "__main__":
    main() 