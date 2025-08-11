#!/usr/bin/env python3
"""
测试优化后的AI生成功能
验证用例数量充足和完整性
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.utils import DeepSeekClient

def test_enhanced_generation():
    """测试优化后的生成功能"""
    print("🧪 开始测试优化后的AI生成功能...")
    
    # 创建客户端
    client = DeepSeekClient()
    
    # 测试需求
    test_requirement = """
    用户管理系统功能需求：
    1. 用户注册：支持邮箱注册，需要验证码验证
    2. 用户登录：支持邮箱/密码登录，支持记住密码
    3. 用户信息管理：查看、编辑个人资料
    4. 密码管理：修改密码，忘记密码重置
    5. 用户权限：普通用户和管理员权限
    """
    
    print(f"📝 测试需求：{test_requirement[:100]}...")
    
    try:
        # 生成测试用例
        print("🚀 开始生成测试用例...")
        result = client.generate_test_cases(
            requirement=test_requirement,
            user_prompt=test_requirement,  # 使用需求作为提示词
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
        
        # 检查完整性
        incomplete_marks = ["...", "等等", "此处省略", "待补充", "未完待续", "待完善"]
        has_incomplete = any(mark in result for mark in incomplete_marks)
        print(f"是否包含省略标记：{'是' if has_incomplete else '否'}")
        
        # 检查用例分布
        positive_count = result.count('正向') + result.count('正常')
        negative_count = result.count('异常') + result.count('错误')
        boundary_count = result.count('边界') + result.count('极限')
        
        print(f"正向测试用例：{positive_count}")
        print(f"异常测试用例：{negative_count}")
        print(f"边界测试用例：{boundary_count}")
        
        # 保存结果
        with open('test_generation_result.md', 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✅ 测试完成！结果已保存到 test_generation_result.md")
        
        # 验证结果
        test_case_count = result.count('TC-')
        if test_case_count >= 20:
            print(f"✅ 用例数量充足：{test_case_count}个")
        else:
            print(f"❌ 用例数量不足：{test_case_count}个（期望≥20个）")
        
        if not has_incomplete:
            print("✅ 内容完整，无省略标记")
        else:
            print("❌ 内容不完整，包含省略标记")
        
        if result.count('## ') >= 3:
            print("✅ 功能模块覆盖充分")
        else:
            print("❌ 功能模块覆盖不足")
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_enhanced_generation()
    sys.exit(0 if success else 1) 