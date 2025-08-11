#!/usr/bin/env python3
"""
测试格式化生成功能
验证输出格式是否符合要求
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.utils import DeepSeekClient

def test_formatted_generation():
    """测试格式化生成功能"""
    print("🧪 开始测试格式化生成功能...")
    
    # 创建客户端
    client = DeepSeekClient()
    
    # 测试需求
    test_requirement = """
    电商系统核心功能需求：
    1. 用户管理：注册、登录、个人信息管理
    2. 商品管理：商品展示、搜索、分类浏览
    3. 购物车：添加商品、修改数量、删除商品
    4. 订单管理：下单、支付、订单查询
    5. 评价系统：商品评价、评分、评论管理
    """
    
    print(f"📝 测试需求：{test_requirement[:100]}...")
    
    try:
        # 生成测试用例
        print("🚀 开始生成格式化测试用例...")
        result = client.generate_test_cases(
            requirement=test_requirement,
            user_prompt=test_requirement,
            is_batch=False,
            batch_id=0,
            total_batches=1
        )
        
        # 分析结果
        print("\n📊 生成结果分析：")
        print(f"总字符数：{len(result)}")
        print(f"测试用例数量：{result.count('TC-')}")
        print(f"功能模块数量：{result.count('## ')}")
        print(f"测试步骤数量：{result.count('测试步骤')}")
        print(f"预期结果数量：{result.count('预期结果')}")
        print(f"测试场景数量：{result.count('测试场景')}")
        print(f"优先级数量：{result.count('优先级')}")
        
        # 检查格式
        print("\n🔍 格式检查：")
        has_title = '# 测试用例文档' in result
        print(f"是否有标题：{'✅' if has_title else '❌'}")
        
        has_modules = '## ' in result
        print(f"是否有模块：{'✅' if has_modules else '❌'}")
        
        has_proper_format = '### TC-' in result and '**测试场景**' in result
        print(f"是否有正确格式：{'✅' if has_proper_format else '❌'}")
        
        has_summary = '总结' in result
        print(f"是否有总结：{'✅' if has_summary else '❌'}")
        
        # 检查完整性
        incomplete_marks = ["...", "等等", "此处省略", "待补充", "未完待续", "待完善"]
        has_incomplete = any(mark in result for mark in incomplete_marks)
        print(f"是否包含省略标记：{'❌' if has_incomplete else '✅'}")
        
        # 检查用例分布
        positive_count = result.count('正向') + result.count('正常')
        negative_count = result.count('异常') + result.count('错误')
        boundary_count = result.count('边界') + result.count('极限')
        
        print(f"\n📈 用例分布：")
        print(f"正向测试用例：{positive_count}")
        print(f"异常测试用例：{negative_count}")
        print(f"边界测试用例：{boundary_count}")
        
        # 保存结果
        with open('test_formatted_result.md', 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✅ 测试完成！结果已保存到 test_formatted_result.md")
        
        # 验证结果
        test_case_count = result.count('TC-')
        if test_case_count >= 50:
            print(f"✅ 用例数量充足：{test_case_count}个")
        else:
            print(f"❌ 用例数量不足：{test_case_count}个（期望≥50个）")
        
        if not has_incomplete:
            print("✅ 内容完整，无省略标记")
        else:
            print("❌ 内容不完整，包含省略标记")
        
        if has_proper_format:
            print("✅ 格式正确，符合要求")
        else:
            print("❌ 格式不正确")
            
        if has_summary:
            print("✅ 包含总结部分")
        else:
            print("❌ 缺少总结部分")
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_formatted_generation()
    sys.exit(0 if success else 1) 