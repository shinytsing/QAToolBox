#!/usr/bin/env python3
"""
测试简单日记页面（不需要认证）
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser

def test_template_without_auth():
    """测试不需要认证的模板渲染"""
    print("🧪 测试模板渲染（不需要认证）...")
    
    try:
        # 创建匿名用户上下文
        context = {
            'today_entry': None,
            'daily_question': '今天最让你印象深刻的颜色是？',
            'recent_achievements': [],
            'streak_days': 0,
            'month_entries_count': 0,
            'today': '2024-01-01',
        }
        
        # 渲染模板
        html = render_to_string('tools/simple_diary_home.html', context)
        
        print(f"✅ 模板渲染成功，内容长度: {len(html)}")
        
        # 检查关键内容
        checks = [
            ('页面标题', '简单生活日记'),
            ('CSS变量', '--text-color: #2c3e50'),
            ('JavaScript函数', 'displayDefaultTemplates'),
            ('统计卡片', '连续记录天数'),
            ('记录方式', '文字记录'),
            ('心情选择器', '😊'),
        ]
        
        for check_name, check_content in checks:
            if check_content in html:
                print(f"✅ {check_name}: 正确")
            else:
                print(f"❌ {check_name}: 不正确")
        
        # 保存HTML到文件以便检查
        with open('simple_diary_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ HTML内容已保存到 simple_diary_output.html")
        
        return True
        
    except Exception as e:
        print(f"❌ 模板渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_template_file():
    """检查模板文件是否存在和内容"""
    print("\n🧪 检查模板文件...")
    
    template_path = 'templates/tools/simple_diary_home.html'
    
    if os.path.exists(template_path):
        print(f"✅ 模板文件存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 模板文件大小: {len(content)} 字符")
        
        # 检查关键内容
        checks = [
            ('页面标题', '简单生活日记'),
            ('CSS变量', '--text-color: #2c3e50'),
            ('JavaScript函数', 'displayDefaultTemplates'),
        ]
        
        for check_name, check_content in checks:
            if check_content in content:
                print(f"✅ {check_name}: 在模板文件中正确")
            else:
                print(f"❌ {check_name}: 在模板文件中不正确")
        
        return True
    else:
        print(f"❌ 模板文件不存在: {template_path}")
        return False

if __name__ == '__main__':
    print("🔍 开始测试简单日记页面（不需要认证）...")
    
    success = True
    success &= check_template_file()
    success &= test_template_without_auth()
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
